# -*- coding: utf8 -*-

"""Admin classes for maps.models."""

from __future__ import unicode_literals
from __future__ import absolute_import

from datetime import datetime

from django.conf import settings
from django.contrib.gis import admin
from django.contrib.gis.geos import Point
from django.contrib.sites.models import Site

from grappelli.forms import GrappelliSortableHiddenMixin
import reversion

from notaro.admin import CurrentSiteAdmin, CODEMIRROR_CSS
from .models import (Place, Url, PlaceNote, PlaceUrl, cleanname, CustomMap,
        CustomMapMarker, )


class OSitesMixin(object):
    """
    Mixin used in the inline admin classes which refer to "site-dependent" models.

    Provides a read only field showing on which sites the related objects exist.
    """

    def get_readonly_fields(self, request, obj=None):
        return ('osites', ) +\
               super(OSitesMixin, self).get_readonly_fields(request, obj)

    def osites(self, obj):
        if obj is None:
            return '-'
        sitelist = ', '.join([s.siteprofile.short_name
                              for s in self.osite_field(obj).sites.exclude(
                                  id=Site.objects.get_current().id)])
        if not Site.objects.get_current() in self.osite_field(obj).sites.all():
            sitelist = '<i class="fa fa-lock" style="font-size: 150%"></i> ' +\
                    sitelist
        return sitelist or '-'
    osites.allow_tags = True
    osites.short_description = 'Andere Familienbäume'


class UrlAdmin(admin.ModelAdmin):
    search_fields = ('title', 'link', )

admin.site.register(Url, UrlAdmin)


class UrlInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = PlaceUrl
    extra = 1

    raw_id_fields = ('url', )
    related_lookup_fields = {'fk': ['url', ], }


class NotePlaceInline(GrappelliSortableHiddenMixin,
                      OSitesMixin, admin.TabularInline):
    """Note Inline class used by PlaceAdmin."""

    model = PlaceNote
    extra = 1
    raw_id_fields = ('note', )
    autocomplete_lookup_fields = {'fk': ['note', ], }
    sortable_excludes = ('position', )

    def osite_field(self, obj):
        return obj.note


class PlaceAdmin(admin.OSMGeoAdmin):
    """The PlaceAdmin class."""

    fieldsets = (
        ('', {'fields': ('title', ), }),
        ('Koordinaten', {'fields': ('location', ), }),
        )

    list_display = ('title', 'first_url', 'handle', )
    search_fields = ('title', )
    inlines = [UrlInline, NotePlaceInline, ]

    def view_on_site(self, obj):
        return obj.get_absolute_url()

    def first_url(self, obj):
        """Method to put thumbnail of portrait into list_display."""

        try:
            url = obj.urls.all().order_by('placeurl__position')[0]
        except:
            return ''

        return '<a href="%s">%s</a>' % (url.link, url.title)

    first_url.allow_tags = True
    first_url.short_description = "URL"

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_actions(self, request):
        actions = super(PlaceAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        if not obj.location and not obj.handle:
            # this is the first attempt to save, and no coordinates were
            # specified, so try to retrieve them using geopy
            from geopy.geocoders import Nominatim
            from django.contrib.gis.geos import fromstr
            geolocator = Nominatim(timeout=2)
            try:
                location = geolocator.geocode(obj.title)
                obj.location = fromstr('POINT(%f %f)' %
                                       (location.longitude, location.latitude))
            except:
                pass

        if not obj.handle:
            obj.handle = 'L_'
            if obj.title:
                obj.handle += cleanname(obj.title)[:20]
            if obj.location:
                obj.handle += str(obj.location.x)[:10] + '_'
                obj.handle += str(obj.location.y)[:10]
            obj.handle = obj.handle[:44]
            obj.handle += u'_' + unicode(datetime.now().microsecond)[:5]
        super(PlaceAdmin, self).save_model(request, obj, form, change)

admin.site.register(Place, PlaceAdmin)


class CustomMapMarkerInline(GrappelliSortableHiddenMixin,
                            admin.TabularInline):
    model = CustomMapMarker
    extra = 2
    raw_id_fields = ('place', )
    autocomplete_lookup_fields = {'fk': ['place', ], }
    sortable_excludes = ('position', 'label_offset_x', 'label_offset_y', )


class CustomMapAdmin(CurrentSiteAdmin, admin.OSMGeoAdmin, reversion.VersionAdmin):
    """Admin class for CustomMap model."""

    fieldsets = (
            ('', {'fields': ('title', 'description', ), }),
            ('Geo-Daten', {'fields': ('refresh', 'bbox', ), }),
            ('Marker', {'classes': ('placeholder custommapmarker_set-group', ),
                        'fields': ()}),
            ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                               'fields': ('sites', ), }), )
    inlines = [CustomMapMarkerInline, ]
    raw_id_fields = ('sites', )
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    list_display = ('id', 'title', 'render_status', 'view_on_site_link', )
    search_fields = ('title', 'description', )
    change_list_template = "admin/change_list_filter_sidebar.html"

    pnt = Point(8, 50.5, srid=4326)
    pnt.transform(3857)
    default_lon, default_lat = pnt.coords
    default_zoom = 5

    class Media:
        css = {'all': ('css/custommap_admin.css', ) + CODEMIRROR_CSS, }
        js = ('codemirror/codemirror-compressed.js',
              'dajaxice/dajaxice.core.js',
              'js/adminactions.js',
              )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except ImportError:
            pass
        js += ('codemirror/codemirror_conf_custommap.js', )

admin.site.register(CustomMap, CustomMapAdmin)

