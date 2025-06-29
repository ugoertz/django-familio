# -*- coding: utf8 -*-

"""Admin classes for notaro.models."""

import datetime
from io import BytesIO
import os
import os.path
import tempfile
import zipfile
import pyclamd
from urllib.parse import quote as urlquote

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.helpers import ActionForm
from django.contrib.sites.models import Site
from django.core.files.storage import default_storage
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import re_path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from filebrowser.base import FileObject
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
        'codemirror/lib/codemirror.css',
        'codemirror/addon/hint/show-hint.css',
        'codemirror/addon/dialog/dialog.css',
        'codemirror-custom/custom.css', )

CODEMIRROR_JS = (
        'codemirror/lib/codemirror.js',
        'codemirror/mode/clike/clike.js',
        'codemirror/mode/python/python.js',
        'codemirror/mode/rst/rst.js',
        'codemirror/mode/stex/stex.js',
        'codemirror/addon/dialog/dialog.js',
        'codemirror/addon/edit/matchbrackets.js',
        'codemirror/addon/mode/overlay.js',
        'codemirror/addon/search/searchcursor.js',
        'codemirror/addon/hint/show-hint.js',
        'codemirror/keymap/vim.js',
        )


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
        return format_html(
                '<a href="{}">Seite ansehen</a>',
                self.view_on_site(obj))
    view_on_site_link.short_description = 'Link'

    def get_urls(self):
        # pylint: disable=no-member
        urls = super().get_urls()
        return [re_path(r'^(?P<pk>\d+)/change/remove/$',
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
            sitelist = mark_safe(
                    '<i class="fa fa-lock" style="font-size: 150%"></i> ' +
                    sitelist)
        return sitelist or '-'
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
        urls = super().get_urls()
        return [re_path(r'^import/$',
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
        js = CODEMIRROR_JS + (
              'js/adminactions.js',
              )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except:
            pass
        js += ('codemirror-custom/codemirror_conf.js', )
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
        js = CODEMIRROR_JS + (
              'js/adminactions.js',
              )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except:
            pass
        js += ('codemirror-custom/codemirror_conf_source.js', )
        css = {'all': ('css/source_admin.css', ) + CODEMIRROR_CSS, }


admin.site.register(Source, SourceAdmin)


class UploadZipFileForm(forms.Form):

    archive = MultiFileField(
            label="Bilddateien (.jpg, .png), "
                  "pdf-Dateien, Archiv-Dateien (.zip)",
            required=True)
    target = forms.ChoiceField(
            choices=(
                ('documents', 'Dokumente'),
                ('images', 'Bilder'),
                ('videos', 'Videos'), ),
            required=True,
            label="Art der Dateien")
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
            label="Automatisch in Datenbank einbinden",
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

            # virus scan
            try:
                scanner = VirusScan()
            except pyclamd.ConnectionError:
                # not ideal -- check for ClamAV connection in
                # handle_file_upload, too
                pass
            else:
                filedata.seek(0)
                result = scanner.cd.scan_stream(filedata)
                if result:
                    # we scanned only one file, so this must be it
                    fn = list(result)[0]
                    info = result[fn]
                    raise forms.ValidationError(
                        ('In der Datei %s wurde der Virus ' % filedata.name) +
                        ('%s gefunden.\n' % ', '.join(info)) +
                        'Die Datei ist auf dem Server gespeichert, '
                        'wurde aber '
                        'nicht in die Datenbank eingefügt. Das kann '
                        'gegebenenfalls manuell im Verwaltungsbereich '
                        'durchgeführt werden.')

            filedata.seek(0)
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


class VirusScan:

    def __init__(self):
        try:
            self.cd = pyclamd.ClamdNetworkSocket(host="clamav")  # for docker
        except:
            self.cd = None

        if not self.cd:
            try:
                self.cd = pyclamd.ClamdAgnostic()
            except:
                self.cd = None

        if not (self.cd and self.cd.ping()):
            raise pyclamd.ConnectionError('Could not connect to clamav.')


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

    def action_checkbox(self, obj):
        """
        A list_display column containing a checkbox widget.
        Override this here because Picture.__str__ includes HTML code for the
        picture thumbnail, and we do not want to put that inside the aria-label.
        """
        attrs = {
            "class": "action-select",
            "aria-label": format_html(
                _("Select this object for an action - {}, {}"),
                str(obj.pk), obj.caption[:40],
            ),
        }
        checkbox = forms.CheckboxInput(attrs, lambda value: False)
        return checkbox.render(helpers.ACTION_CHECKBOX_NAME, str(obj.pk))

    def get_changeform_initial_data(self, request):
        return {'sites': [request.site, ], }

    def image_thumbnail(self, obj):
        """Display thumbnail, to be used in django admin list_display."""

        if obj.image and obj.image.filetype == "Image":
            return format_html(
                    '<img src="{}" />',
                    obj.image.version_generate(ADMIN_THUMBNAIL).url)
        else:
            return ""
    image_thumbnail.short_description = "Thumbnail"

    list_display = ('id', 'caption', 'date', 'image_thumbnail', )

    def get_urls(self):
        # pylint: disable=no-member
        urls = super().get_urls()
        return [re_path(r'^uploadarchive/$',
                    self.admin_site.admin_view(self.upload_archive),
                    name="uploadarchive"),
                re_path(r'^virusscanall/$',
                    self.admin_site.admin_view(self.scan_all),
                    name="scanall"),
                ] + urls

    def scan_all(self, request):
        results = ''

        try:
            scanner = VirusScan()
        except pyclamd.ConnectionError:
            messages.error(
                    request,
                    'Verbindung zum Virenscanner fehlgeschlagen')
            return render(
                    request,
                    'customadmin/scanall.html',
                    {'results': results, })

        results = scanner.cd.multiscan_file(os.path.join(
            settings.MEDIA_ROOT,
            settings.FILEBROWSER_DIRECTORY))

        return render(request, 'customadmin/scanall.html',
                      {'results': results, })

    def handle_file_upload(
            self, request, filedata, path, target, create_objects):

        filename = convert_filename(os.path.basename(filedata.name))
        if target == 'images':
            if filename[-4:].lower() not in ['.jpg', '.png', ]:
                messages.warning(
                        request,
                        'Es wurden keine Dateien hochgeladen. '
                        'Erlaubt: .jpg, .png')
                return
        elif target == 'videos':
            if filename[-4:].lower() not in ['.mp4', '.ogv', 'webm', '.vob']:
                messages.warning(
                        request,
                        'Es wurden keine Dateien hochgeladen. '
                        'Erlaubt: .mp4, .ogv, .webm, .vob')
                return
        elif target == 'documents':
            if filename[-4:].lower() not in [
                    '.pdf', '.doc', '.rtf', '.jpg', '.png',
                    '.tif', '.mp3', '.mp4', 'docx', '.odt']:
                messages.warning(
                        request,
                        'Es wurden keine Dateien hochgeladen. '
                        'Erlaubt: .pdf, .doc(x), .rtf, .jpg, '
                        '.png, .tif, .mp3/4')
                return

        store_path = os.path.join(
                settings.FILEBROWSER_DIRECTORY,
                target,
                path,
        )
        full_path = os.path.join(settings.MEDIA_ROOT, store_path)

        # There is a small risk of a race condition here (if the same
        # user tries to upload files twice at the same time from
        # different forms ...). We ignore this problem.
        try:
            os.makedirs(full_path)
        except OSError:
            if not os.path.isdir(full_path):
                raise

        final_path = default_storage.save(
                os.path.join(store_path, filename),
                filedata)

        if create_objects:
            try:
                VirusScan()
            except pyclamd.ConnectionError:
                messages.warning(
                        request,
                        'Verbindung zum Virenscanner fehlgeschlagen.')
            obj_path = final_path
                       # was: os.path.relpath(final_path, settings.MEDIA_ROOT)

            if target == 'images':
                # pylint: disable=no-member
                picture = Picture.objects.create(
                        image=FileObject(obj_path))
                # assert Picture.objects.all().count() == pl + 1
                picture.sites.add(Site.objects.get_current())
            elif target == 'videos':
                # pylint: disable=no-member
                video = Video.objects.create(video=FileObject(obj_path))
                video.sites.add(Site.objects.get_current())

                compile_video(video.id)
            elif target == 'documents':
                # pylint: disable=no-member
                doc = Document.objects.create(doc=FileObject(obj_path))
                doc.sites.add(Site.objects.get_current())
                doc.name = doc.doc.filename_root

                # can we "generate" a thumbnail?
                # (could use imagemagick to generate thumbnail for pdfs, but it
                # seems that only rarely the first page is the desired
                # thumbnail, and it seems hard to automatically find a more
                # suitable one)
                if filename[-4:].lower() in ['.jpg', '.png', '.tif', ]:
                    doc.image = doc.doc

                doc.save()

    def upload_archive(self, request):
        if request.method == 'POST':
            form = UploadZipFileForm(request.POST, request.FILES)
            if form.is_valid():
                path = form.cleaned_data['path']
                target = form.cleaned_data['target']

                for filedata in form.cleaned_data['archive']:
                    if filedata.name.endswith('.zip'):
                        zipf = zipfile.ZipFile(filedata, 'r')
                        for fn in zipf.infolist():
                            self.handle_file_upload(
                                    request,
                                    zipf.open(fn),
                                    path,
                                    target,
                                    create_objects=form.cleaned_data[
                                        'create_objects'])
                        zipf.close()
                    else:
                        self.handle_file_upload(
                                request,
                                filedata,
                                path,
                                target,
                                create_objects=form.cleaned_data[
                                    'create_objects'])

                if form.cleaned_data['create_objects']:
                    tgt = {
                            'images': 'picture',
                            'videos': 'video',
                            'documents': 'document',
                            }[target]
                    if target == 'documents':
                        return HttpResponseRedirect(
                                reverse(
                                    'document-list-ordered',
                                    kwargs={'order_by': 'added'}))
                    else:
                        tgt = {
                                'images': 'picture',
                                'videos': 'video',
                                }[target]
                        return HttpResponseRedirect(
                                reverse('%s-list' % tgt))

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
        js = CODEMIRROR_JS + (
              'js/adminactions.js',
              )
        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except:
            pass
        js += ('codemirror-custom/codemirror_conf_pic_vid.js', )
        css = {'all': ('css/picture_admin.css', ) + CODEMIRROR_CSS, }


admin.site.register(Picture, PictureAdmin)


class DocumentAdmin(CurrentSiteAdmin, VersionAdmin):
    """Admin class for Document model."""

    fieldsets = (('', {'fields': ('name', 'description',
                                  'doc', 'image', 'date', ), }),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('sites', )
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    list_filter = ('sites', )
    search_fields = ('description', )

    def image_thumbnail(self, obj):
        """Display thumbnail, to be used in django admin list_display."""

        if obj.image and obj.image.filetype == "Image":
            return format_html(
                    '<img src="{}" />',
                    obj.image.version_generate(ADMIN_THUMBNAIL).url)
        else:
            return ""
    image_thumbnail.short_description = "Thumbnail"

    list_display = ('id', 'name', 'description_truncated', 'filename',
                    'date', 'image_thumbnail', 'view_on_site_link')

    def description_truncated(self, obj):
        return obj.description[:50]

    def filename(self, obj):
        return obj.doc.filename

    class Media:
        js = CODEMIRROR_JS + (
              'js/adminactions.js',
              )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except:
            pass
        js += ('codemirror-custom/codemirror_conf_document.js', )
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

    def action_checkbox(self, obj):
        """
        A list_display column containing a checkbox widget.
        Override this here because Picture.__str__ includes HTML code for the
        picture thumbnail, and we do not want to put that inside the aria-label.
        """
        attrs = {
            "class": "action-select",
            "aria-label": format_html(
                _("Select this object for an action - {}, {}"),
                str(obj.pk), obj.caption[:40],
            ),
        }
        checkbox = forms.CheckboxInput(attrs, lambda value: False)
        return checkbox.render(helpers.ACTION_CHECKBOX_NAME, str(obj.pk))

    def image_thumbnail(self, obj):
        """Display thumbnail, to be used in django admin list_display."""

        if obj.poster and obj.poster.filetype == "Image":
            return format_html(
                    '<img src="{}" />',
                    obj.poster.version_generate(ADMIN_THUMBNAIL).url)
        else:
            return ""
    image_thumbnail.short_description = "Thumbnail"

    list_display = ('id', 'caption', 'date', 'image_thumbnail',
                    'view_on_site_link')

    def filename(self, obj):
        return obj.video.filename

    def recompile_video(self, request, pk):
        compile_video(pk)
        self.message_user(request,
                          'Die Videodateien werden neu erstellt.')
        return HttpResponseRedirect(reverse(
            'admin:%s_%s_changelist' %
            (self.model._meta.app_label, self.model._meta.model_name)))

    def get_urls(self):
        # pylint: disable=no-member
        urls = super().get_urls()
        return [re_path(r'^(?P<pk>\d+)/change/recompile/$',
                    self.admin_site.admin_view(self.recompile_video)),
                ] + urls

    class Media:
        js = CODEMIRROR_JS + (
              )
        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except:
            pass
        js += ('codemirror-custom/codemirror_conf_pic_vid.js', )
        css = {'all': ('css/picture_admin.css', ) + CODEMIRROR_CSS, }


admin.site.register(Video, VideoAdmin)
