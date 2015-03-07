# -*- coding: utf8 -*-

"""Admin classes for genealogio.models."""

from __future__ import unicode_literals
from __future__ import absolute_import
from datetime import datetime

from django.contrib.gis import admin
from django.forms.models import BaseInlineFormSet
from django.conf import settings
from django.contrib.sites.models import Site
# from django.core.exceptions import ObjectDoesNotExist
# from django.utils.functional import curry
import reversion
from filebrowser.settings import ADMIN_THUMBNAIL
from grappelli.forms import GrappelliSortableHiddenMixin

from accounts.models import UserSite
from notaro.admin import CurrentSiteAdmin
from .models import (Person, Place, Event, Family, Name, PersonEvent,
                     PersonFamily, FamilyEvent, PlaceUrl, Url,
                     PersonPlace, PersonNote, FamilyNote, EventNote,
                     PlaceNote, )


class OSitesMixin(object):
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


class EventInline(OSitesMixin, admin.TabularInline):
    """Event Inline class used by PersonAdmin."""

    model = PersonEvent
    extra = 0
    raw_id_fields = ('event', )
    autocomplete_lookup_fields = {'fk': ['event', ], }

    def osite_field(self, obj):
        return obj.event


class FamilyPInline(GrappelliSortableHiddenMixin,
                    OSitesMixin, admin.TabularInline):
    """Family Inline class used by PersonAdmin."""

    model = PersonFamily
    extra = 0
    raw_id_fields = ('family', )
    autocomplete_lookup_fields = {'fk': ['family', ], }
    sortable_excludes = ('position', 'child_type', )
    verbose_name = "Familie"
    verbose_name_plural = "Familien"

    def osite_field(self, obj):
        return obj.family


class NotePInline(GrappelliSortableHiddenMixin,
                  OSitesMixin, admin.TabularInline):
    """Note Inline class used by PersonAdmin."""

    model = PersonNote
    extra = 1
    raw_id_fields = ('note', )
    autocomplete_lookup_fields = {'fk': ['note', ], }
    sortable_excludes = ('position', )

    def osite_field(self, obj):
        return obj.note


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


class PPlaceInline(admin.StackedInline):
    """Inline class for PersonPlace used by PersonAdmin."""

    formset = PPlaceFormSet
    model = PersonPlace
    extra = 2
    fields = (('place', 'typ', ), ('start', 'end', ), 'comment', )
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


class PersonAdmin(CurrentSiteAdmin, reversion.VersionAdmin):
    """The PersonAdmin class."""

    fieldsets = (
        ('Name', {'classes': ('placeholder name_set-group', ), 'fields': ()}),
        ('', {'fields': (('datebirth', 'datedeath', ),
                         ('gender_type', 'probably_alive', ), ), }),
        ('Orte', {'classes': ('placeholder personplace_set-group', ),
                  'fields': ()}),
        ('Weitere Informationen', {'fields': (('portrait', 'portrait_os'),
                                              'comments', ), }),
        ('Familien', {'classes': ('placeholder personfamily_set-group', ),
                      'fields': ()}),
        ('Texte', {'classes': ('placeholder personnote_set-group', ),
                   'fields': ()}),
        ('Ereignisse', {'classes': ('placeholder personevent_set-group', ),
                        'fields': ()}),
        ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                            'fields': ('sites', ), }),
        )

    list_display = ('last_name', 'first_name', 'datebirth', 'placebirth',
                    'datedeath', 'placedeath', 'image_thumbnail', 'handle',
                    'view_on_site', )

    inlines = [NameInline, FamilyPInline, EventInline, NotePInline,
               SourcePInline, PPlaceInline, ]
    raw_id_fields = ('portrait', 'sites', )
    related_lookup_fields = {'fk': ['portrait', ], }
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    search_fields = ('handle', 'datebirth', 'datedeath',
                     'name__name', 'places__title',)
    list_filter = ('gender_type', 'probably_alive', 'name__name', 'sites', )
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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "sites" and not request.user.is_superuser:
            kwargs["queryset"] = request.user.userprofile.sites.filter(
                    usersite__role__in=[UserSite.STAFF, UserSite.SUPERUSER, ])
        return super(PersonAdmin, self).formfield_for_manytomany(
                db_field, request, **kwargs)

    def portrait_os(self, obj):
        sitelist = ', '.join([s.siteprofile.short_name
                              for s in obj.portrait.sites.exclude(
                                  id=Site.objects.get_current().id)])
        if not Site.objects.get_current() in obj.portrait.sites.all():
            sitelist = '<i class="fa fa-lock" style="font-size: 150%"></i> ' +\
                    sitelist
        return sitelist or '-'
    portrait_os.allow_tags = True
    portrait_os.short_description = 'Andere Familienbäume'

    def view_on_site(self, obj):
        '''Put link to person's detail view into changelist.'''
        return '<a href="%s">Seite ansehen</a>' % obj.get_absolute_url()
    view_on_site.allow_tags = True
    view_on_site.short_description = 'Link'

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return super(PersonAdmin, self).get_readonly_fields(request, obj)

        rof = ()
        if obj.portrait and request.site not in obj.portrait.sites.all():
            rof += ('portrait', )

        return rof + super(PersonAdmin, self).get_readonly_fields(request, obj)

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
              'dajaxice/dajaxice.core.js',
              'js/adminactions.js', )

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


class SourceEInline(admin.TabularInline):
    """The SourceEInline class."""

    # pylint: disable=no-member
    model = Event.source.through
    extra = 0


class FamilyEInline(admin.TabularInline):
    """The FamilyEInline class (Family-inline in EventAdmin)."""

    fields = ('family', 'role', )
    model = FamilyEvent
    extra = 0
    raw_id_fields = ('family', )
    autocomplete_lookup_fields = {'fk': ['family', ]}
    verbose_name = "Beteiligte Familie"
    verbose_name_plural = "Beteiligte Familien"


class EventPInline(admin.TabularInline):
    """Person Inline class used by EventAdmin."""

    model = PersonEvent
    extra = 0
    sortable_excludes = ('role', )
    raw_id_fields = ('person', )
    autocomplete_lookup_fields = {'fk': ['person', ], }
    verbose_name = "Beteiligte Person"
    verbose_name_plural = "Beteiligte Personen"


class NoteEInline(GrappelliSortableHiddenMixin,
                  OSitesMixin, admin.TabularInline):
    """Note Inline class used by EventAdmin."""

    model = EventNote
    extra = 1
    raw_id_fields = ('note', )
    autocomplete_lookup_fields = {'fk': ['note', ], }
    sortable_excludes = ('position', )

    def osite_field(self, obj):
        return obj.note


class EventAdmin(CurrentSiteAdmin, reversion.VersionAdmin):
    """The EventAdmin class."""

    fieldsets = (
        ('', {'fields': ('title', 'event_type', 'date',
                         'description', 'place')}),
        ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                            'fields': ('sites', ), }),
        )
    inlines = [EventPInline, FamilyEInline, NoteEInline, SourceEInline, ]
    raw_id_fields = ('place', 'sites', )
    autocomplete_lookup_fields = {'fk': ['place', ],
                                  'm2m': ['sites', ]}
    list_display = ('title', 'date', 'place', 'handle', )
    search_fields = ('title', 'description', )
    list_filter = ('event_type', 'sites', )
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
              'dajaxice/dajaxice.core.js',
              'js/adminactions.js', )

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


class PersonFInline(GrappelliSortableHiddenMixin,
                    OSitesMixin, admin.TabularInline):
    """Person Inline class used by FamilyAdmin."""

    model = PersonFamily
    extra = 0
    fieldsets = (('', {'fields': ('person', 'child_type',
                                  'osites', 'position', ), }), )
    raw_id_fields = ('person', )
    autocomplete_lookup_fields = {'fk': ['person', ], }
    sortable_excludes = ('position', 'child_type', )
    verbose_name = "Kind"
    verbose_name_plural = "Kinder"

    def osite_field(self, obj):
        return obj.person


class EventFInline(GrappelliSortableHiddenMixin,
                   OSitesMixin, admin.TabularInline):
    """The EventFInline class (Events-inline in FamilyAdmin)."""

    model = FamilyEvent
    extra = 0
    raw_id_fields = ('event', )
    autocomplete_lookup_fields = {'fk': ['event', ]}
    sortable_excludes = ('position', )

    def osite_field(self, obj):
        return obj.event


class NoteFInline(GrappelliSortableHiddenMixin,
                  OSitesMixin, admin.TabularInline):
    """Note Inline class used by EventAdmin."""

    model = FamilyNote
    extra = 1
    raw_id_fields = ('note', )
    autocomplete_lookup_fields = {'fk': ['note', ], }
    sortable_excludes = ('position', )

    def osite_field(self, obj):
        return obj.note


class FamilyAdmin(CurrentSiteAdmin, reversion.VersionAdmin):
    """The FamilyAdmin class."""

    fieldsets = (
        ('', {'fields': ('name',
                         ('father', 'father_os', ),
                         ('mother', 'mother_os', ), )}),
        ('Daten', {'classes': ('grp-collapse grp-open', ),
                   'fields': ('family_rel_type',
                              ('start_date', 'end_date', ), )}),
        ('Familienbäume', {'classes': ('grp-collapse grp-closed', ),
                            'fields': ('sites', ), }),
        )
    inlines = [PersonFInline, EventFInline, NoteFInline, SourceFInline, ]
    raw_id_fields = ('father', 'mother', 'sites', )
    autocomplete_lookup_fields = {
            'fk': ['father', 'mother', ],
            'm2m': ['sites', ], }
    search_fields = ('handle', 'name',
                     'father__name__name', 'mother__name__name', )
    list_filter = ('sites', )
    readonly_fields = ('father_os', 'mother_os', )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return super(FamilyAdmin, self).get_readonly_fields(request, obj)

        rof = ()
        if obj.father and request.site not in obj.father.sites.all():
            rof += ('father', )
        if obj.mother and request.site not in obj.mother.sites.all():
            rof += ('mother', )

        return rof + super(FamilyAdmin, self).get_readonly_fields(request, obj)

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

    def father_os(self, obj):
        sitelist = ', '.join([s.siteprofile.short_name
                              for s in obj.father.sites.exclude(
                                  id=Site.objects.get_current().id)])
        if not Site.objects.get_current() in obj.father.sites.all():
            sitelist = '<i class="fa fa-lock" style="font-size: 150%"></i> ' +\
                    sitelist
        return sitelist or '-'
    father_os.allow_tags = True
    father_os.short_description = 'Andere Familienbäume'

    def mother_os(self, obj):
        sitelist = ', '.join([s.siteprofile.short_name
                              for s in obj.mother.sites.exclude(
                                  id=Site.objects.get_current().id)])
        if not Site.objects.get_current() in obj.mother.sites.all():
            sitelist = '<i class="fa fa-lock" style="font-size: 150%"></i> ' +\
                    sitelist
        return sitelist or '-'
    mother_os.allow_tags = True
    mother_os.short_description = 'Andere Familienbäume'

    class Media:
        css = {'all': ('css/family_admin.css', ), }
        js = ('js/adminactions.js', )


admin.site.register(Family, FamilyAdmin)
