# -*- coding: utf8 -*-

"""Admin classes for notaro.models."""

from __future__ import unicode_literals
from __future__ import absolute_import

from django.contrib import admin
from django.conf import settings
import reversion
from filebrowser.settings import ADMIN_THUMBNAIL
# from grappelli.forms import GrappelliSortableHiddenMixin

from .models import Note, Picture, Source


class SourceNInline(admin.TabularInline):
    """Inline class to put Note-Source into Note's detail page."""

    # pylint: disable=no-member
    model = Note.source.through
    extra = 0


class NoteAdmin(reversion.VersionAdmin):
    """Admin class for Note model."""

    fieldsets = (('', {'fields': ('title', 'link', 'text',
                                  'published', 'authors', ), }),
                 ('Bilder', {'fields': ('pictures', ), }),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('authors', 'pictures', 'sites', )
    related_lookup_fields = {'m2m': ['authors', 'pictures', ], }
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    inlines = [SourceNInline, ]
    list_display = ('link', 'title', 'view_on_site', )
    list_filter = ('sites', )
    search_fields = ('title', 'text', )

    def get_queryset(self, request):
        qs = super(NoteAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(sites=request.site)

    def get_changeform_initial_data(self, request):
        return {'sites': [request.site, ], }

    def get_readonly_fields(self, request, obj=None):
        if obj is None or request.user.is_superuser:
            return self.readonly_fields
        else:
            return ('sites',) + self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_actions(self, request):
        actions = super(NoteAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

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
              'dajaxice/dajaxice.core.js', )

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


class SourceAdmin(reversion.VersionAdmin):
    """Admin class for Source model."""
    pass

admin.site.register(Source, SourceAdmin)


class PictureAdmin(reversion.VersionAdmin):
    """Admin class for Picture model."""

    fieldsets = (('', {'fields': ('caption', 'image', 'date', ), }),
                 ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                                     'fields': ('sites', ), }), )
    raw_id_fields = ('sites', )
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    list_filter = ('sites', )
    search_fields = ('caption', )

    def get_queryset(self, request):
        qs = super(PictureAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(sites=request.site)

    def get_changeform_initial_data(self, request):
        return {'sites': [request.site, ], }

    def get_readonly_fields(self, request, obj=None):
        if obj is None or request.user.is_superuser:
            return self.readonly_fields
        else:
            return ('sites',) + self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_actions(self, request):
        actions = super(PictureAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def image_thumbnail(self, obj):
        """Display thumbnail, to be used in django admin list_display."""

        if obj.image and obj.image.filetype == "Image":
            return '<img src="%s" />'\
                   % obj.image.version_generate(ADMIN_THUMBNAIL).url
        else:
            return ""
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = "Thumbnail"

    list_display = ['id', 'caption', 'date', 'image_thumbnail', ]

admin.site.register(Picture, PictureAdmin)
