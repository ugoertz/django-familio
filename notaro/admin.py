# -*- coding: utf8 -*-

"""Admin classes for notaro.models."""

from __future__ import unicode_literals
from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django import forms
import reversion
from filebrowser.settings import ADMIN_THUMBNAIL
from grappelli.forms import GrappelliSortableHiddenMixin

from base.models import SiteProfile
from accounts.models import UserSite
from .models import Note, Picture, Source, PictureNote


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
                role__in=[UserSite.STAFF, UserSite.SUPERUSER]).count():
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
        if not obj.authors.count():
            # no authors yet, so save current user as author
            obj.authors.add(request.user)

    def view_on_site(self, obj):
        '''Put link to note's detail view into changelist.'''
        return '<a href="%s">Seite ansehen</a>' % obj.get_absolute_url()
    view_on_site.allow_tags = True
    view_on_site.short_description = 'Link'

    class Media:
        js = ('codemirror/codemirror.js',
              'codemirror/show-hint.js',
              'codemirror/python.js',
              'codemirror/stex.js',
              'codemirror/overlay.js',
              'codemirror/rst.js',
              'dajaxice/dajaxice.core.js',
              'js/adminactions.js'
              )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except ImportError:
            pass
        js += ('codemirror/codemirror_conf.js', )
        css = {'all': ('codemirror/codemirror.css',
                       # 'codemirror/docs.css',
                       'codemirror/show-hint.css',
                       'codemirror/custom.css', ), }

admin.site.register(Note, NoteAdmin)


class SourceAdmin(CurrentSiteAdmin, reversion.VersionAdmin):
    """Admin class for Source model."""

    class Media:
        js = ('js/adminactions.js', )


admin.site.register(Source, SourceAdmin)


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

    class Media:
        js = ('js/adminactions.js', )


admin.site.register(Picture, PictureAdmin)
