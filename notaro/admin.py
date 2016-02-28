# -*- coding: utf8 -*-

"""Admin classes for notaro.models."""

from __future__ import unicode_literals
from __future__ import absolute_import

import datetime
from io import BytesIO
import os
import os.path
import tempfile
import zipfile

from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.contrib.sites.models import Site
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import urlquote

from filebrowser.settings import ADMIN_THUMBNAIL
from filebrowser.utils import convert_filename
from grappelli.forms import GrappelliSortableHiddenMixin
from reversion.admin import VersionAdmin

from base.fields import MultiFileField
from base.models import SiteProfile
from accounts.models import UserSite
from .models import (Note, Picture, Source, PictureNote, NoteSource,
                     PictureSource, Document, Video, VideoSource, )
from .tasks import compile_video


CODEMIRROR_CSS = (
        'codemirror/codemirror.css',
        'codemirror/show-hint.css',
        'codemirror/dialog.css',
        'codemirror/custom.css', )


class UpdateActionForm(ActionForm):
    site = forms.ModelChoiceField(queryset=SiteProfile.objects.all(),
                                  empty_label="(Keine Auswahl)",
                                  required=False)


class CurrentSiteAdmin(object):
    """
    A mixin for modeladmin classes which

    - sets reasonable default for sites field when new instances are created,
      and makes the field readonly on edits
    - removes the delete action
    - adds a "remove object" action (which removes the object from the current
      site),
    - add a "add to other site" action (for users which also have staff status
      at the other site)
    - displays list of all sites where this object lives in changelist
    """

    action_form = UpdateActionForm
    change_form_template = "customadmin/change_form.html"

    def view_on_site(self, obj):
        try:
            return obj.get_absolute_url()
        except AttributeError:
            return

    def view_on_site_link(self, obj):
        '''Put link to detail view into changelist.'''
        return '<a href="%s">Seite ansehen</a>' % self.view_on_site(obj)
    view_on_site_link.allow_tags = True
    view_on_site_link.short_description = 'Link'

    def get_urls(self):
        # pylint: disable=no-member
        urls = super(CurrentSiteAdmin, self).get_urls()
        return [url(r'^(?P<pk>\d+)/remove/$',
                    self.admin_site.admin_view(self.remove_object)),
                ] + urls

    def remove_object(self, request, pk):
        # pylint: disable=no-member
        obj = self.model.objects.get(pk=pk)
        obj.sites.remove(request.site)
        self.message_user(request,
                          'Der Eintrag wurde aus diesem '
                          'Familienbaum entfernt.')
        return HttpResponseRedirect(reverse(
            'admin:%s_%s_changelist' %
            (self.model._meta.app_label, self.model._meta.model_name)))

    def ositelist(self, obj):
        sitelist = ', '.join([s.siteprofile.short_name
                              for s in obj.sites.exclude(
                                  id=Site.objects.get_current().id)])
        if not Site.objects.get_current() in obj.sites.all():
            sitelist = '<i class="fa fa-lock" style="font-size: 150%"></i> ' +\
                    sitelist
        return sitelist or '-'
    ositelist.allow_tags = True
    ositelist.short_description = 'Andere Familienbäume'

    def get_list_display(self, request):
        # pylint: disable=no-member
        return self.list_display + ('ositelist', )

    def get_queryset(self, request):
        # pylint: disable=no-member
        qs = super(CurrentSiteAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(sites=request.site)

    def get_changeform_initial_data(self, request):
        return {'sites': [request.site, ] +
                list(request.site.siteprofile.neighbor_sites.all()), }

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def addsite_selected(self, request, queryset):
        # pylint: disable=no-member
        siteprofile_id = request.POST['site']
        try:
            site = Site.objects.get(siteprofile=siteprofile_id)
        except:
            self.message_user(
                    request,
                    "Kein Familienbaum ausgewählt.")
            return

        if not request.user.is_superuser and\
            not UserSite.objects.filter(
                user=request.user.userprofile,
                site=site,
                role__in=[UserSite.STAFF, UserSite.SUPERUSER]).exists():
            self.message_user(
                    request,
                    "Diese Aktion erfordert Redakteursstatus "
                    "für den Familienbaum %s." % site.siteprofile.short_name)
            return

        for object in queryset:
            object.sites.add(site)

        # pylint: disable=no-member
        self.message_user(
                request,
                "%d Objekte dem Familienbaum %s hinzugefügt."
                % (queryset.count(), site.siteprofile.short_name))

    addsite_selected.short_description =\
        'Ausgewählte Objekte dem ausgewählten Familienbaum hinzufügen'

    def remove_selected(self, request, queryset):
        for object in queryset:
            object.sites.remove(request.site)

        # pylint: disable=no-member
        self.message_user(request, "%d Objekte entfernt." % queryset.count())

    remove_selected.short_description =\
        'Ausgewählte Objekte aus diesem Familienbaum entfernen'

    def get_actions(self, request):
        # pylint: disable=no-member
        actions = super(CurrentSiteAdmin, self).get_actions(request)

        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        actions['addsite_selected'] = (
                CurrentSiteAdmin.addsite_selected,
                'addsite_selected',
                CurrentSiteAdmin.addsite_selected.short_description)
        actions['remove_selected'] = (
                CurrentSiteAdmin.remove_selected,
                'remove_selected',
                CurrentSiteAdmin.remove_selected.short_description)
        return actions

    def get_readonly_fields(self, request, obj=None):
        # pylint: disable=no-member
        if obj is None or request.user.is_superuser:
            return self.readonly_fields
        else:
            return ('sites',) + self.readonly_fields


class SourceNInline(admin.TabularInline):
    """Inline class to put Note-Source into Note's detail page."""

    # pylint: disable=no-member
    model = NoteSource
    extra = 0
    raw_id_fields = ('source', )
    autocomplete_lookup_fields = {'fk': ['source', ], }
    verbose_name = "Quellenangabe"
    verbose_name_plural = "Quellenangaben"


class PictureNInline(GrappelliSortableHiddenMixin,
                     admin.TabularInline):
    """Inline class to put Note-Source into Note's detail page."""

    # pylint: disable=no-member
    model = PictureNote
    sortable_excludes = ('position', )
    raw_id_fields = ('picture', )
    related_lookup_fields = {'fk': ['picture', ], }
    extra = 1

    class Meta:
        verbose_name = 'Bild'
        verbose_name_plural = 'Bilder'


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=200,
                            label="Titel",
                            widget=forms.TextInput(
                                attrs={'style': 'width: 100%;', }))
    upfile = forms.FileField(label="Datei")
    fmt = forms.ChoiceField(
            label="Format",
            choices=(('docx', 'Microsoft Word docx'),
                     ('html', 'HTML'),))


class NoteAdmin(CurrentSiteAdmin, VersionAdmin):
    """Admin class for Note model."""

    fieldsets = (('', {'fields': ('title', 'link', 'text',
                                  'published', 'authors', ), }),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('authors', 'pictures', 'sites', )
    related_lookup_fields = {'m2m': ['authors', 'pictures', ], }
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    inlines = [PictureNInline, SourceNInline, ]
    list_display = ('link', 'title', 'published', 'view_on_site_link', )
    list_filter = ('published', 'sites', )
    search_fields = ('title', 'text', )
    change_list_template = "admin/change_list_filter_sidebar.html"

    def save_related(self, request, form, formset, change):
        super(NoteAdmin, self).save_related(request, form, formset, change)
        obj = form.instance
        if not obj.authors.exists():
            # no authors yet, so save current user as author
            obj.authors.add(request.user)

    def get_urls(self):
        # pylint: disable=no-member
        urls = super(NoteAdmin, self).get_urls()
        return [url(r'^import/$',
                    self.admin_site.admin_view(self.import_object),
                    name="importnote"),
                ] + urls

    def import_object(self, request):
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                path = tempfile.mkdtemp(
                        dir=os.path.join(settings.PROJECT_ROOT, 'tmp'))
                f = request.FILES['upfile']
                with open(
                        os.path.join(path,
                                     'original.%s'
                                     % form.cleaned_data['fmt']), 'wb')\
                        as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)

                title = form.cleaned_data['title']
                rstfile = os.path.join(path, 'result.rst')
                os.system(
                    'cd %s && pandoc -f %s -t rst original.%s > result.rst' %
                    (path,
                     form.cleaned_data['fmt'], form.cleaned_data['fmt'], ))
                return HttpResponseRedirect(reverse(
                    'admin:%s_%s_add' %
                    (self.model._meta.app_label,
                     self.model._meta.model_name)) +
                    '?title=%s&rstfile=%s' %
                    (urlquote(title), os.path.join(path, rstfile)))
        else:
            form = UploadFileForm()
        return render(request, 'customadmin/import.html',
                      {'form': form, 'title': 'Text importieren'})

    def get_changeform_initial_data(self, request):
        initial = super(NoteAdmin, self).get_changeform_initial_data(request)
        initial['sites'] = [request.site, ]

        if 'rstfile' in request.GET:
            with open(request.GET['rstfile']) as f:
                rst = f.read()
                initial.update({'text': rst, 'published': False, })
        initial.update({'title': request.GET.get('title', ''), })

        return initial

    class Media:
        js = ('codemirror/codemirror-compressed.js',
              'dajaxice/dajaxice.core.js',
              'js/adminactions.js',
              )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except ImportError:
            pass
        js += ('codemirror/codemirror_conf.js', )
        css = {'all': ('css/note_admin.css', ) + CODEMIRROR_CSS, }

admin.site.register(Note, NoteAdmin)


class SourceAdmin(CurrentSiteAdmin, VersionAdmin):
    """Admin class for Source model."""

    fieldsets = (('', {'fields':
                       ('name', 'description', 'confidence_level', ), }),
                 ('Dokumente', {'fields': ('documents', )}),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('documents', 'sites', )
    autocomplete_lookup_fields = {'m2m': ['documents', 'sites', ], }
    list_display = ('name', 'confidence_level', 'view_on_site_link', )
    search_fields = ('name', 'description', )
    change_list_template = "admin/change_list_filter_sidebar.html"

    class Media:
        js = ('codemirror/codemirror-compressed.js',
              'dajaxice/dajaxice.core.js',
              'js/adminactions.js',
              )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except ImportError:
            pass
        js += ('codemirror/codemirror_conf_source.js', )
        css = {'all': ('css/source_admin.css', ) + CODEMIRROR_CSS, }


admin.site.register(Source, SourceAdmin)


class UploadZipFileForm(forms.Form):

    archive = MultiFileField(
            label="Bilddateien (.jpg, .png), "
                  "pdf-Dateien, Archiv-Dateien (.zip)",
            required=True)
    path = forms.CharField(
            max_length=50,
            required=True,
            label="Pfad",
            help_text='Unterverzeichnis, in dem die Bilder gespeichert werden '
            'sollen. Es muss ein Pfad angegeben werden. Zum Beispiel: '
            '<span style="font-family: courier, monospace;">ug2015-06</span> '
            'oder <span style="font-family: courier, monospace;">'
            'personen/mast/123</span>.',
            widget=forms.TextInput(attrs={'style': 'width: 100%;', }))
    create_objects = forms.BooleanField(
            label="Automatisch Bildobjekte erstellen",
            required=False,
            initial=True)

    def clean_path(self):
        path = self.cleaned_data['path']
        for forbidden in ['..', '\\', ':']:
            if path.find(forbidden) != -1:
                raise forms.ValidationError(
                        'Pfad darf nicht "%s" enthalten.' % forbidden)
        if path.find('\n') != -1 or path.find('\r') != -1:
            raise forms.ValidationError(
                    'Pfad darf keine Zeilenumbrüche enthalten.')
        if path.startswith('/'):
            raise forms.ValidationError(
                    'Pfad darf nicht mit "/" beginnen.')

        return path

    def clean(self):
        cleaned_data = super(UploadZipFileForm, self).clean()
        for required_field in ['archive', 'path', ]:
            if required_field not in cleaned_data:
                return cleaned_data

        errors = []
        for filedata in cleaned_data['archive']:
            # sanitize uploaded files:
            # FIXME: pdf, doc, ...

            if filedata.name[-4:] in ['.jpg', '.png']:
                # from django.forms.fields.ImageField
                from PIL import Image

                if hasattr(filedata, 'temporary_file_path'):
                    file = filedata.temporary_file_path()
                else:
                    if hasattr(filedata, 'read'):
                        file = BytesIO(filedata.read())
                    else:
                        file = BytesIO(filedata['content'])

                try:
                    image = Image.open(file)
                    image.verify()
                except:
                    errors.append(
                            'Die Datei %s konnte nicht eingelesen werden.'
                            % filedata.name)

            if filedata.name.endswith('.zip') and\
                    not zipfile.is_zipfile(filedata):
                errors.append(
                        'Die Datei %s ist kein zip-Archiv.' % filedata.name)
        if errors:
            raise forms.ValidationError(' '.join(errors))

        return cleaned_data


class SourcePictureInline(admin.TabularInline):
    """Inline class to put Picture-Source into Picture's detail page."""

    # pylint: disable=no-member
    model = PictureSource
    extra = 0
    raw_id_fields = ('source', )
    autocomplete_lookup_fields = {'fk': ['source', ], }
    verbose_name = "Quellenangabe"
    verbose_name_plural = "Quellenangaben"


class PictureAdmin(CurrentSiteAdmin, VersionAdmin):
    """Admin class for Picture model."""

    fieldsets = (('', {'fields': ('caption', 'image', 'date', ), }),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('sites', )
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    list_filter = ('sites', )
    search_fields = ('caption', )
    inlines = [SourcePictureInline, ]

    def get_changeform_initial_data(self, request):
        return {'sites': [request.site, ], }

    def image_thumbnail(self, obj):
        """Display thumbnail, to be used in django admin list_display."""

        if obj.image and obj.image.filetype == "Image":
            return '<img src="%s" />'\
                   % obj.image.version_generate(ADMIN_THUMBNAIL).url
        else:
            return ""
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = "Thumbnail"

    list_display = ('id', 'caption', 'date', 'image_thumbnail', )

    def get_urls(self):
        # pylint: disable=no-member
        urls = super(PictureAdmin, self).get_urls()
        return [url(r'^uploadarchive/$',
                    self.admin_site.admin_view(self.upload_archive),
                    name="uploadarchive"),
                ] + urls

    def handle_file_upload(self, filedata, path, create_objects):
        filename = convert_filename(os.path.basename(filedata.name))
        if filename[-4:].lower() in ['.jpg', '.png', ]:
            target = 'images'
        elif filename[-4:].lower() in [
                '.pdf', '.doc', '.rtf',
                '.tif', '.mp3', 'docx']:
            target = 'documents'
        elif filename[-4:].lower() in [
                '.mp4', '.ogg', '.webm', '.vob', ]:
            target = 'videos'
        else:
            return

        full_path = os.path.join(
                settings.MEDIA_ROOT,
                settings.FILEBROWSER_DIRECTORY,
                target,
                path)

        # There is a small risk of a race condition here (if the same
        # user tries to upload files twice at the same time from
        # different forms ...). We ignore this problem.
        try:
            os.makedirs(full_path)
        except OSError:
            if not os.path.isdir(full_path):
                raise

        default_storage.save(
                os.path.join(full_path, filename),
                filedata)
        if create_objects:
            if target == 'images':
                picture_path = os.path.join(
                        settings.FILEBROWSER_DIRECTORY, target, path, filename)
                # pylint: disable=no-member
                picture = Picture.objects.create(image=picture_path)
                picture.sites.add(Site.objects.get_current())
            if target == 'videos':
                # create video object
                video_path = os.path.join(
                        settings.FILEBROWSER_DIRECTORY, target, path, filename)
                # pylint: disable=no-member
                video = Video.objects.create(video=video_path)
                video.sites.add(Site.objects.get_current())

                compile_video(video.id)

        # return information whether we uploaded an image or a document
        return target

    def upload_archive(self, request):
        if request.method == 'POST':
            form = UploadZipFileForm(request.POST, request.FILES)
            if form.is_valid():
                path = form.cleaned_data['path']

                target = None

                # check whether among all uploaded files there was at least one
                # image (one document, resp.) (the final redirect will depend
                # on this)
                uploaded_images = False
                uploaded_documents = False
                uploaded_videos = False

                for filedata in form.cleaned_data['archive']:
                    if filedata.name.endswith('.zip'):
                        zipf = zipfile.ZipFile(filedata, 'r')
                        for fn in zipf.infolist():
                            target = self.handle_file_upload(
                                    zipf.open(fn),
                                    path,
                                    form.cleaned_data['create_objects'])
                            if target == 'images':
                                uploaded_images = True
                            elif target == 'documents':
                                uploaded_documents = True
                            elif target == 'videos':
                                uploaded_videos = True
                        zipf.close()
                    else:
                        target = self.handle_file_upload(
                                filedata,
                                path,
                                form.cleaned_data['create_objects'])
                        if target == 'images':
                            uploaded_images = True
                        elif target == 'documents':
                            uploaded_documents = True
                        elif target == 'videos':
                            uploaded_videos = True

                if uploaded_images:
                    if form.cleaned_data['create_objects']:
                        return HttpResponseRedirect(reverse('picture-list'))
                    else:
                        target = 'images'
                if uploaded_videos:
                    if form.cleaned_data['create_objects']:
                        return HttpResponseRedirect(reverse('video-list'))
                    else:
                        target = 'images'
                if not (uploaded_images or
                        uploaded_documents or
                        uploaded_videos):
                    messages.warning(
                            request,
                            'Es wurden keine Dateien hochgeladen. '
                            'Erlaubt: .jpg, .png, .pdf, .zip, '
                            '.doc, .rtf, .docx, .mp3, .mp4, .ogg, .webm, .vob')
                    return HttpResponseRedirect(reverse('admin:uploadarchive'))

                return HttpResponseRedirect(
                            '/admin/filebrowser/browse/?&dir=' +
                            os.path.join(target, path))
        else:
            initial_path = '%s/' % request.user.username
            initial_path += datetime.datetime.now().strftime('%Y/%m-%d')
            form = UploadZipFileForm(initial={'path': initial_path, })
        return render(request, 'customadmin/uploadarchive.html',
                      {'form': form, 'title': 'Bilder/Dokumente hochladen'})

    class Media:
        js = ('js/adminactions.js', )
        css = {'all': ('css/picture_admin.css', ), }


admin.site.register(Picture, PictureAdmin)


class DocumentAdmin(CurrentSiteAdmin, VersionAdmin):
    """Admin class for Document model."""

    fieldsets = (('', {'fields': ('name', 'description', 'doc', 'date', ), }),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('sites', )
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    list_filter = ('sites', )
    search_fields = ('description', )
    list_display = ('id', 'description_truncated', 'filename',
                    'date', 'view_on_site_link')

    def description_truncated(self, obj):
        return obj.description[:50]

    def filename(self, obj):
        return obj.doc.filename

    class Media:
        js = ('codemirror/codemirror-compressed.js',
              'dajaxice/dajaxice.core.js',
              'js/adminactions.js',
              )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except ImportError:
            pass
        js += ('codemirror/codemirror_conf_document.js', )
        css = {'all': ('css/document_admin.css', ) + CODEMIRROR_CSS, }


admin.site.register(Document, DocumentAdmin)


class SourceVideoInline(admin.TabularInline):
    """Inline class to put Video-Source into Video's detail page."""

    # pylint: disable=no-member
    model = VideoSource
    extra = 0
    raw_id_fields = ('source', )
    autocomplete_lookup_fields = {'fk': ['source', ], }
    verbose_name = "Quellenangabe"
    verbose_name_plural = "Quellenangaben"


class VideoAdmin(CurrentSiteAdmin, VersionAdmin):
    """Admin class for Video model."""

    fieldsets = (('', {'fields': ('caption', 'video', 'poster', 'date', ), }),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('sites', )
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    list_filter = ('sites', )
    search_fields = ('caption', )
    inlines = [SourceVideoInline, ]

    def image_thumbnail(self, obj):
        """Display thumbnail, to be used in django admin list_display."""

        if obj.poster and obj.poster.filetype == "Image":
            return '<img src="%s" />'\
                   % obj.poster.version_generate(ADMIN_THUMBNAIL).url
        else:
            return ""
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = "Thumbnail"

    list_display = ('id', 'caption', 'date', 'image_thumbnail', )

    def filename(self, obj):
        return obj.video.filename

    class Media:
        js = ('codemirror/codemirror-compressed.js',
              'dajaxice/dajaxice.core.js',
              'js/adminactions.js',
              )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except ImportError:
            pass
        js += ('codemirror/codemirror_conf_document.js', )
        css = {'all': ('css/document_admin.css', ) + CODEMIRROR_CSS, }


admin.site.register(Video, VideoAdmin)
