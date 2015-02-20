# -*- coding: utf8 -*-

"""Admin classes for genealogio.models."""

from __future__ import unicode_literals
from __future__ import absolute_import
from datetime import datetime

from django.contrib.gis import admin
from django.forms.models import BaseInlineFormSet
from django.conf import settings
# from django.utils.functional import curry
import reversion
from filebrowser.settings import ADMIN_THUMBNAIL
from grappelli.forms import GrappelliSortableHiddenMixin

from .models import Person, Place, Event, Family, Name, PersonEvent
from .models import PersonFamily, FamilyEvent, PlaceUrl, Url
from .models import PersonPlace


def cleanname(name):
    """Replace umlauts (ä by ae, etc.) and then remove all non-ASCII letters
    from string."""

    for umlaut, expansion in [('Ä', 'Ae'), ('Ö', 'Oe'), ('Ü', 'Ue'),
                              ('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'),
                              ('ß', 'ss'), ]:
        name = name.replace(umlaut, expansion)
    return u''.join([c for c in name
                     if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
                     'abcdefghijklmnopqrstuvwxyz'])


class NameFormSet(BaseInlineFormSet):
    """FormSet for the different Names of a Person.
    """

    def __init__(self, *args, **kwargs):
        super(NameFormSet, self).__init__(*args, **kwargs)

        # Check that the data doesn't already exist
        if not kwargs['instance'].name_set.count():
            self.initial = [{'typ': Name.FIRSTNAME, },
                            {'typ': Name.BIRTHNAME, },
                            {'typ': Name.MARRIEDNAME, }, ]
            # Make enough extra formsets to hold initial forms


class NameInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    """Inline class to put Names of a Person into the Person's detail page."""

    model = Name
    formset = NameFormSet
    extra = 3
    fields = ('name', 'typ', 'position', )
    sortable_excludes = ('position', 'typ', )
    search_fields = ('name', )

    def get_extra(self, request, obj=None, **kwargs):
        """Dynamically sets the number of extra forms. 0 if the related object
        already exists or the extra configuration otherwise."""

        if obj:
            # Don't add any extra forms if the related object already exists.
            return 0
        return self.extra


class SourcePInline(admin.TabularInline):
    """Inline class to put Person-Source into Person's detail page."""

    # pylint: disable=no-member
    model = Person.source.through
    extra = 0


class EventInline(admin.TabularInline):
    """Event Inline class used by PersonAdmin."""

    model = PersonEvent
    extra = 0
    raw_id_fields = ('event', )
    autocomplete_lookup_fields = {'fk': ['event', ], }


class FamilyPInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    """Family Inline class used by PersonAdmin."""

    model = PersonFamily
    extra = 0
    raw_id_fields = ('family', )
    autocomplete_lookup_fields = {'fk': ['family', ], }
    sortable_excludes = ('position', 'child_type', )


class PPlaceFormSet(BaseInlineFormSet):
    """FormSet for the different Places of a Person.
    """

    def __init__(self, *args, **kwargs):
        super(PPlaceFormSet, self).__init__(*args, **kwargs)

        try:
            # Check that the data doesn't already exist
            if not kwargs['instance'].places.count():
                self.initial = [{'typ': PersonPlace.BIRTH, },
                                {'typ': PersonPlace.DEATH, }, ]
        except ValueError:
            # Cannot access places yet, so we are newly adding a Person
            self.initial = [{'typ': PersonPlace.BIRTH, },
                            {'typ': PersonPlace.DEATH, }, ]


class PPlaceInline(admin.TabularInline):
    """Inline class for PersonPlace used by PersonAdmin."""

    formset = PPlaceFormSet
    model = PersonPlace
    extra = 2
    fields = ('place', 'typ', 'start', 'end', 'comment', )
    raw_id_fields = ('place', )
    autocomplete_lookup_fields = {'fk': ['place', ], }
    sortable_excludes = ('typ', )

    def get_extra(self, request, obj=None, **kwargs):
        """Dynamically sets the number of extra forms, depending on whether the
        related object already exists or the extra configuration otherwise."""

        if obj and obj.places.count():
            # Add no extra forms if the related object already exists.
            return 0
        return self.extra


class PersonAdmin(reversion.VersionAdmin):
    """The PersonAdmin class."""

    fieldsets = (
        ('Name', {'classes': ('placeholder name_set-group', ), 'fields': ()}),
        ('', {'fields': ('gender_type', 'probably_alive', ), }),
        ('Daten', {'fields': ('datebirth',
                              'datedeath', ), }),
        ('Orte', {'classes': ('placeholder personplace_set-group', ),
                  'fields': ()}),
        ('Dokumente', {'fields': ('portrait', 'notes', 'comments', ), }),
        ('Verschiedenes', {'classes': ('grp-collapse grp-closed', ),
                           'fields': ('private', 'public', ),
                           }),
        )

    list_display = ('last_name', 'first_name', 'datebirth', 'placebirth',
                    'datedeath', 'placedeath', 'image_thumbnail', 'handle',
                    'view_on_site', )

    inlines = [NameInline, FamilyPInline, EventInline,
               SourcePInline, PPlaceInline, ]
    raw_id_fields = ('portrait', 'notes', )
    related_lookup_fields = {'fk': ['portrait', ], }
    autocomplete_lookup_fields = {'m2m': ['notes', ], }
    search_fields = ('handle', 'datebirth', 'datedeath',
                     'name__name', 'places__title',)
    list_filter = ('gender_type', 'probably_alive', 'name__name', )
    change_list_template = "admin/change_list_filter_sidebar.html"

    def image_thumbnail(self, obj):
        """Method to put thumbnail of portrait into list_display."""

        if obj.portrait and obj.portrait.image and\
                obj.portrait.image.filetype == "Image":
            return '<img src="%s" />'\
                   % obj.portrait.image.version_generate(ADMIN_THUMBNAIL).url
        else:
            return ""
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = "Portrait"

    def view_on_site(self, obj):
        '''Put link to person's detail view into changelist.'''
        return '<a href="%s">Seite ansehen</a>' % obj.get_absolute_url()
    view_on_site.allow_tags = True
    view_on_site.short_description = 'Link'

    def save_model(self, request, obj, form, change):
        if not obj.handle:
            obj.handle = 'P_'
            try:
                obj.handle += cleanname(request.POST['name_set-1-name'])[:20]
            except KeyError:
                pass
            try:
                obj.handle += cleanname(request.POST['name_set-2-name'])[:20]
            except KeyError:
                pass
            try:
                obj.handle += cleanname(request.POST['name_set-0-name'])[:20]
            except KeyError:
                pass
            if obj.datebirth:
                obj.handle += unicode(obj.datebirth.year)
            if obj.datedeath:
                obj.handle += unicode(obj.datedeath.year)
            obj.handle = obj.handle[:44]
            obj.handle += u'_' + unicode(datetime.now().microsecond)[:5]
        super(PersonAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formset, change):
        super(PersonAdmin, self).save_related(request, form, formset, change)
        obj = form.instance
        try:
            obj.last_name = obj.name_set.filter(typ__in=[Name.BIRTHNAME,
                                                         Name.MARRIEDNAME,
                                                         Name.TAKEN, ])[0].name
        except:
            pass
        try:
            obj.first_name = obj.name_set.filter(typ__in=[Name.FIRSTNAME,
                                                          Name.RUFNAME,
                                                          Name.NICKNAME,
                                                          ])[0].name
        except:
            pass
        obj.save()

    class Media:
        css = {'all': ('css/person_admin.css', 
                       'codemirror/codemirror.css',
                       'codemirror/show-hint.css',
                       'codemirror/custom.css', ), }
        js = ('codemirror/codemirror.js',
              'codemirror/show-hint.js',
              'codemirror/python.js',
              'codemirror/stex.js',
              'codemirror/overlay.js',
              'codemirror/rst.js',
              'dajaxice/dajaxice.core.js', )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except:
            pass
        js += ('codemirror/codemirror_conf_person.js', )


admin.site.register(Person, PersonAdmin)


class UrlAdmin(admin.ModelAdmin):
    search_fields = ('title', 'link', )

admin.site.register(Url, UrlAdmin)


class UrlInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = PlaceUrl
    extra = 1

    raw_id_fields = ('url', )
    related_lookup_fields = {'fk': ['url', ], }


class PlaceAdmin(admin.OSMGeoAdmin):
    """The PlaceAdmin class."""

    fieldsets = (
        ('', {'fields': ('title', ), }),
        ('Koordinaten', {'fields': ('location', ), }),
        )

    list_display = ('title', 'first_url', 'handle', )
    search_fields = ('title', )
    inlines = [UrlInline, ]

    def first_url(self, obj):
        """Method to put thumbnail of portrait into list_display."""

        try:
            url = obj.urls.all().order_by('placeurl__position')[0]
        except:
            return ''

        return '<a href="%s">%s</a>' % (url.link, url.title)

    first_url.allow_tags = True
    first_url.short_description = "URL"

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


class SourceEInline(admin.TabularInline):
    """The SourceEInline class."""

    # pylint: disable=no-member
    model = Event.source.through
    extra = 0


class EventFInline(admin.TabularInline):
    """The EventFInline class."""

    model = FamilyEvent
    extra = 0


class EventPInline(admin.TabularInline):
    """Person Inline class used by EventAdmin."""

    model = PersonEvent
    extra = 0
    sortable_excludes = ('role', )
    raw_id_fields = ('person', )
    autocomplete_lookup_fields = {'fk': ['person', ], }


class EventAdmin(reversion.VersionAdmin):
    """The EventAdmin class."""

    fieldsets = (
        ('', {'fields': ('title', 'event_type', 'date',
                         'description', 'place')}),
        )
    inlines = [EventPInline, EventFInline, SourceEInline, ]
    raw_id_fields = ('place', )
    autocomplete_lookup_fields = {'fk': ['place', ], }
    list_display = ('title', 'date', 'place', 'handle', )
    search_fields = ('title', 'description', )
    list_filter = ('event_type', )
    change_list_template = "admin/change_list_filter_sidebar.html"

    def save_model(self, request, obj, form, change):
        if not obj.handle:
            obj.handle = 'E_'
            obj.handle += cleanname(obj.title)[:20]
            if obj.date:
                obj.handle += unicode(obj.date.year)
            if obj.place:
                obj.handle += cleanname(obj.place.title)[:20]
            obj.handle = obj.handle[:44]
            obj.handle += u'_' + unicode(datetime.now().microsecond)[:5]
        super(EventAdmin, self).save_model(request, obj, form, change)

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
        except:
            pass
        js += ('codemirror/codemirror_conf_event.js', )
        css = {'all': ('css/event_admin.css',
                       'codemirror/codemirror.css',
                       # 'codemirror/docs.css',
                       'codemirror/show-hint.css',
                       'codemirror/custom.css', ), }


admin.site.register(Event, EventAdmin)


class SourceFInline(admin.TabularInline):
    """Inline class: Source for Family."""

    # pylint: disable=no-member
    model = Family.source.through
    extra = 0


class PersonFInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    """Person Inline class used by FamilyAdmin."""

    model = PersonFamily
    extra = 0
    fields = ('person', 'child_type', 'position', )
    raw_id_fields = ('person', )
    autocomplete_lookup_fields = {'fk': ['person', ], }
    sortable_excludes = ('position', 'child_type', )


class FamilyAdmin(reversion.VersionAdmin):
    """The FamilyAdmin class."""

    fieldsets = (
        ('', {'fields': ('name', 'father', 'mother', 'family_rel_type', )}),
        ('Daten', {'classes': ('grp-collapse grp-closed', ),
                   'fields': ('start_date', 'end_date', )}),
        )
    inlines = [PersonFInline, EventFInline, SourceFInline, ]
    raw_id_fields = ('father', 'mother', )
    autocomplete_lookup_fields = {'fk': ['father', 'mother', ], }
    search_fields = ('handle', 'name',
                     'father__name__name', 'mother__name__name', )

    def save_model(self, request, obj, form, change):
        """Create handle before saving Family instance."""

        if not obj.handle:
            obj.handle = 'F_'
            try:
                obj.handle += cleanname(obj.father.last_name)
                if obj.father.datebirth:
                    obj.handle += unicode(obj.father.datebirth.year)
            except:
                pass
            try:
                obj.handle += cleanname(obj.mother.last_name)
                if obj.mother.datebirth:
                    obj.handle += unicode(obj.mother.datebirth.year)
            except:
                pass
            obj.handle = u'%s_%s' % (
                         obj.handle[:44],
                         unicode(datetime.now().microsecond)[:5])

        super(FamilyAdmin, self).save_model(request, obj, form, change)

    class Media:
        css = {'all': ('css/family_admin.css', ), }


admin.site.register(Family, FamilyAdmin)
