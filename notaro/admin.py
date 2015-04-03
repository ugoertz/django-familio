# -*- coding: utf8 -*-

"""Admin classes for notaro.models."""

from __future__ import unicode_literals
from __future__ import absolute_import

import os
import os.path
import tempfile
import zipfile

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import urlquote
from django import forms
import reversion
from filebrowser.settings import ADMIN_THUMBNAIL
from grappelli.forms import GrappelliSortableHiddenMixin

from base.models import SiteProfile
from accounts.models import UserSite
from .models import Note, Picture, Source, PictureNote


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

    action_form = UpdateActionForm
    change_form_template = "customadmin/change_form.html"

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
            print object, request.site

        # pylint: disable=no-member
        self.message_user(request, "%d Objekte entfernt." % queryset.count())

    remove_selected.short_description =\
        'Ausgewählte Objekte aus diesem Familienbaum entfernen'

    def get_actions(self, request):
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
    model = Note.source.through
    extra = 0


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
    fmt = forms.ChoiceField(label="Format",
            choices=(('docx', 'Microsoft Word docx'),
                     ('html', 'HTML'),))


class NoteAdmin(CurrentSiteAdmin, reversion.VersionAdmin):
    """Admin class for Note model."""

    fieldsets = (('', {'fields': ('title', 'link', 'text',
                                  'published', 'authors', ), }),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('authors', 'pictures', 'sites', )
    related_lookup_fields = {'m2m': ['authors', 'pictures', ], }
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    inlines = [PictureNInline, SourceNInline, ]
    list_display = ('link', 'title', 'view_on_site', )
    list_filter = ('sites', )
    search_fields = ('title', 'text', )

    def save_related(self, request, form, formset, change):
        super(NoteAdmin, self).save_related(request, form, formset, change)
        obj = form.instance
        if not obj.authors.exists():
            # no authors yet, so save current user as author
            obj.authors.add(request.user)

    def view_on_site(self, obj):
        '''Put link to note's detail view into changelist.'''
        return '<a href="%s">Seite ansehen</a>' % obj.get_absolute_url()
    view_on_site.allow_tags = True
    view_on_site.short_description = 'Link'

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
                with open(os.path.join(path,
                    'original.%s' % form.cleaned_data['fmt']), 'wb')\
                            as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)

                title = form.cleaned_data['title']
                rstfile = os.path.join(path, 'result.rst')
                os.system(
                    'cd %s && pandoc -f %s -t rst original.%s > result.rst' %
                    (path, form.cleaned_data['fmt'], form.cleaned_data['fmt'], ))
                return HttpResponseRedirect(reverse(
                    'admin:%s_%s_add' %
                    (self.model._meta.app_label, self.model._meta.model_name)) +
                    '?title=%s&rstfile=%s' %
                    (urlquote(title), os.path.join(path, rstfile)))
        else:
            form = UploadFileForm()
        return render(request, 'customadmin/import.html',
                {'form': form, 'title': 'Text importieren'})

    def get_changeform_initial_data(self, request):
        initial = super(NoteAdmin, self).get_changeform_initial_data(request)
        if 'rstfile' in request.GET:
            with open(request.GET['rstfile']) as f:
                rst = f.read()
                initial.update({'text': rst, 'published': False })
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


class SourceAdmin(CurrentSiteAdmin, reversion.VersionAdmin):
    """Admin class for Source model."""

    class Media:
        js = ('js/adminactions.js', )


admin.site.register(Source, SourceAdmin)


class UploadZipFileForm(forms.Form):
    path = forms.CharField(
            max_length=50,
            required=False,
            label="Pfad",
            help_text="Wenn ein Pfad angegeben wird, werden die"
                      " Bilder in einem eigenen Unterverzeichnis gespeichert.",
            widget=forms.TextInput(attrs={'style': 'width: 100%;', }))
    archive = forms.FileField(label="Archiv-Datei (.zip)")
    target = forms.ChoiceField(
            label="Inhalt der zip-Datei",
            choices=(('images', 'Bilddateien'),
                     ('documents', 'Dokumente')))


class PictureAdmin(CurrentSiteAdmin, reversion.VersionAdmin):
    """Admin class for Picture model."""

    fieldsets = (('', {'fields': ('caption', 'image', 'date', ), }),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('sites', )
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    list_filter = ('sites', )
    search_fields = ('caption', )

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

    def upload_archive(self, request):
        if request.method == 'POST':
            form = UploadZipFileForm(request.POST, request.FILES)
            if form.is_valid():
                path = form.cleaned_data.get('path', '')
                zipf = zipfile.ZipFile(request.FILES['archive'], 'r')
                print zipf.namelist()
                target_path = os.path.join(settings.MEDIA_ROOT,
                                           settings.FILEBROWSER_DIRECTORY,
                                           form.cleaned_data['target'],
                                           path)
                print 'extract to', target_path
                zipf.extractall(target_path)
                zipf.close()

                return HttpResponseRedirect(
                            '/admin/filebrowser/browse/?&dir=' +
                            os.path.join(form.cleaned_data['target'], path))
        else:
            form = UploadZipFileForm()
        return render(request, 'customadmin/uploadarchive.html',
                {'form': form, 'title': 'Zip-Archiv importieren'})

    class Media:
        js = ('js/adminactions.js', )
        css = {'all': ('css/picture_admin.css', ), }


admin.site.register(Picture, PictureAdmin)
