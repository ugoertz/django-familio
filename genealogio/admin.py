# -*- coding: utf8 -*-

"""Admin classes for genealogio.models."""

from datetime import datetime

from django.conf import settings
from django.conf.urls import url
from django.contrib.gis import admin
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.safestring import mark_safe
# from django.core.exceptions import ObjectDoesNotExist
# from django.utils.functional import curry
from reversion.admin import VersionAdmin
from filebrowser.settings import ADMIN_THUMBNAIL
from grappelli.forms import GrappelliSortableHiddenMixin

from accounts.models import UserSite
from maps.admin import OSitesMixin
from maps.models import cleanname
from notaro.admin import CurrentSiteAdmin, CODEMIRROR_CSS, CODEMIRROR_JS
from .models import (Person, Event, Family, Name, PersonEvent,
                     PersonFamily, FamilyEvent,
                     PersonPlace, PersonNote, FamilyNote, EventNote,
                     TimelineItem, FamilySource,
                     PersonSource, EventSource)


class CurrentSiteGenAdmin(CurrentSiteAdmin):

    def reset_handle(self, request, pk):
        # pylint: disable=no-member
        obj = self.model.objects.get(pk=pk)

        if request.user.is_superuser:
            try:
                obj.reset_handle()
                self.message_user(request, 'Neues handle: %s' % obj.handle)
            except:
                self.message_user(request, 'Es ist ein Fehler aufgetreten.')
        else:
            self.message_user(request,
                              'Diese Aktion darf nur ein superuser ausführen')
        return HttpResponseRedirect(reverse(
            'admin:%s_%s_change' %
            (self.model._meta.app_label, self.model._meta.model_name),
            args=[obj.pk, ]))

    def get_urls(self):
        # pylint: disable=no-member
        urls = super(CurrentSiteGenAdmin, self).get_urls()
        return [url(r'^(?P<pk>\d+)/resethandle/$',
                    self.admin_site.admin_view(self.reset_handle)),
                ] + urls


class NameFormSet(BaseInlineFormSet):
    """FormSet for the different Names of a Person.
    """

    def __init__(self, *args, **kwargs):
        super(NameFormSet, self).__init__(*args, **kwargs)

        # Check that the data doesn't already exist
        if not kwargs['instance'].name_set.exists():
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


class SourcePInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    """Inline class to put Person-Source into Person's detail page."""

    # pylint: disable=no-member
    model = PersonSource
    extra = 0
    raw_id_fields = ('source', )
    autocomplete_lookup_fields = {'fk': ['source', ], }
    verbose_name = "Quellenangabe"
    verbose_name_plural = "Quellenangaben"
    sortable_excludes = ('position', )


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
            if not kwargs['instance'].places.exists():
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
    inline_classes = ('collapse open',)

    def get_extra(self, request, obj=None, **kwargs):
        """Dynamically sets the number of extra forms, depending on whether the
        related object already exists or the extra configuration otherwise."""

        if obj and obj.places.exists():
            # Add no extra forms if the related object already exists.
            return 0
        return self.extra


class PersonAdmin(CurrentSiteGenAdmin, VersionAdmin):
    """The PersonAdmin class."""

    fieldsets = (
        ('Name', {'classes': ('placeholder name_set-group', ), 'fields': ()}),
        ('', {'fields': (('datebirth', 'datedeath', ),
                         ('gender_type', 'probably_alive', ), ), }),
        ('Orte', {'classes': ('placeholder grp-open personplace_set-group', ),
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
                    'view_on_site_link', )

    inlines = [NameInline, FamilyPInline, EventInline, NotePInline,
               SourcePInline, PPlaceInline, ]
    raw_id_fields = ('portrait', 'sites', )
    related_lookup_fields = {'fk': ['portrait', ], }
    autocomplete_lookup_fields = {'m2m': ['sites', ], }
    search_fields = ('handle', 'datebirth', 'datedeath',
                     'name__name', 'places__title',)
    list_filter = ('gender_type', 'probably_alive', 'name__name', 'sites', )
    change_list_template = "admin/change_list_filter_sidebar.html"
    readonly_fields = ('portrait_os', )

    def image_thumbnail(self, obj):
        """Method to put thumbnail of portrait into list_display."""

        if obj.portrait and obj.portrait.image and\
                obj.portrait.image.filetype == "Image":
            return format_html(
                    '<img src="{}" />',
                    obj.portrait.image.version_generate(ADMIN_THUMBNAIL).url)
        else:
            return ""
    image_thumbnail.short_description = "Portrait"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "sites" and not request.user.is_superuser:
            kwargs["queryset"] = request.user.userprofile.sites.filter(
                    usersite__role__in=[UserSite.STAFF, UserSite.SUPERUSER, ])
        return super(PersonAdmin, self).formfield_for_manytomany(
                db_field, request, **kwargs)

    def portrait_os(self, obj):
        sitelist = ', '.join(
                s.siteprofile.short_name
                for s in obj.portrait.sites.exclude(
                    id=Site.objects.get_current().id))
        if not Site.objects.get_current() in obj.portrait.sites.all():
            sitelist = mark_safe(
                    '<i class="fa fa-lock" style="font-size: 150%"></i> ' +\
                    sitelist)
        return sitelist or '-'
    portrait_os.short_description = 'Andere Familienbäume'

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return super(PersonAdmin, self).get_readonly_fields(request, obj)

        rof = ()
        if obj.portrait and request.site not in obj.portrait.sites.all():
            rof += ('portrait', )

        return rof + super(PersonAdmin, self).get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.handle:
            last_name, first_name, married_name = '', '', ''
            for k in request.POST:
                if not (k.startswith('name_set-') and k.endswith('-name')):
                    continue
                try:
                    _, i, _ = k.split('-')
                    i = int(i)
                except:
                    continue

                typ = int(request.POST.get('name_set-%d-typ' % i, -2))
                if typ == Name.BIRTHNAME:
                    last_name = request.POST['name_set-%d-name' % i]
                elif typ == Name.FIRSTNAME:
                    first_name = request.POST['name_set-%d-name' % i]
                elif typ == Name.MARRIEDNAME:
                    married_name = request.POST['name_set-%d-name' % i]
                    if last_name == '':
                        last_name = married_name

            obj.handle = Person.get_handle(
                    last_name=last_name,
                    first_name=first_name,
                    married_name=married_name,
                    datebirth=obj.datebirth,
                    datedeath=obj.datedeath)
        super(PersonAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formset, change):
        super(PersonAdmin, self).save_related(request, form, formset, change)
        obj = form.instance
        try:
            obj.last_name = obj.name_set.filter(
                    typ__in=[Name.BIRTHNAME,
                             Name.MARRIEDNAME,
                             Name.TAKEN, ]).order_by('typ')[0].name
        except:
            pass
        try:
            # Use reverse() here because we want the most recent marriedname
            # (in case there is more than one).
            obj.last_name_current = obj.name_set.filter(
                    typ=Name.MARRIEDNAME).reverse()[0].name
        except:
            obj.last_name_current = obj.last_name
        try:
            obj.first_name = obj.name_set.filter(typ__in=[Name.FIRSTNAME,
                                                          Name.RUFNAME,
                                                          Name.NICKNAME,
                                                          ])[0].name
        except:
            pass
        obj.save()

    class Media:
        css = {'all': ('css/person_admin.css', ) + CODEMIRROR_CSS, }
        js = CODEMIRROR_JS + (
              'js/adminactions.js', )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except:
            pass
        js += ('codemirror-custom/codemirror_conf_person.js', )


admin.site.register(Person, PersonAdmin)


class SourceEInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    """The SourceEInline class."""

    # pylint: disable=no-member
    model = EventSource
    extra = 0
    raw_id_fields = ('source', )
    autocomplete_lookup_fields = {'fk': ['source', ], }
    verbose_name = "Quellenangabe"
    verbose_name_plural = "Quellenangaben"
    sortable_excludes = ('position', )


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


class EventAdmin(CurrentSiteGenAdmin, VersionAdmin):
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
    list_display = ('title', 'date', 'place', 'handle', 'view_on_site_link', )
    search_fields = ('title', 'description', )
    list_filter = ('event_type', 'sites', )
    change_list_template = "admin/change_list_filter_sidebar.html"

    def save_model(self, request, obj, form, change):
        if not obj.handle:
            obj.handle = 'E_'
            obj.handle += cleanname(obj.title)[:20]
            if obj.date:
                obj.handle += str(obj.date.year)
            if obj.place:
                obj.handle += cleanname(obj.place.title)[:20]
            obj.handle = obj.handle[:44]
            obj.handle += u'_' + str(datetime.now().microsecond)[:5]
        super(EventAdmin, self).save_model(request, obj, form, change)

    class Media:
        js = CODEMIRROR_JS + (
              'js/adminactions.js', )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except:
            pass
        js += ('codemirror-custom/codemirror_conf_event.js', )
        css = {'all': ('css/event_admin.css', ) + CODEMIRROR_CSS, }


admin.site.register(Event, EventAdmin)


class SourceFInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    """Inline class: Source for Family."""

    # pylint: disable=no-member
    model = FamilySource
    extra = 0
    raw_id_fields = ('source', )
    autocomplete_lookup_fields = {'fk': ['source', ], }
    verbose_name = "Quellenangabe"
    verbose_name_plural = "Quellenangaben"
    sortable_excludes = ('position', )


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


class FamilyAdmin(CurrentSiteGenAdmin, VersionAdmin):
    """The FamilyAdmin class."""

    fieldsets = (
        ('', {'fields': ('name',
                         ('father', 'father_os', ),
                         ('mother', 'mother_os', ),
                         'comments', )}),
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
    list_display = ('__str__', 'handle', 'view_on_site_link')
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

    def father_os(self, obj):
        sitelist = ', '.join([s.siteprofile.short_name
                              for s in obj.father.sites.exclude(
                                  id=Site.objects.get_current().id)])
        if not Site.objects.get_current() in obj.father.sites.all():
            sitelist = mark_safe(
                    '<i class="fa fa-lock" style="font-size: 150%"></i> ' +\
                    sitelist)
        return sitelist or '-'
    father_os.short_description = 'Andere Familienbäume'

    def mother_os(self, obj):
        sitelist = ', '.join([s.siteprofile.short_name
                              for s in obj.mother.sites.exclude(
                                  id=Site.objects.get_current().id)])
        if not Site.objects.get_current() in obj.mother.sites.all():
            sitelist = mark_safe(
                    '<i class="fa fa-lock" style="font-size: 150%"></i> ' +\
                    sitelist)
        return sitelist or '-'
    mother_os.short_description = 'Andere Familienbäume'

    class Media:
        css = {'all': ('css/family_admin.css', ), }
        js = ('js/adminactions.js', )


admin.site.register(Family, FamilyAdmin)


class TimelineItemAdmin(CurrentSiteAdmin, VersionAdmin):
    fieldsets = (
        ('', {'fields': ('title', ('typ', 'start_date', 'end_date'),
                         'url', 'description', ), }),
        ('Familienbäume, Familien', {'classes': ('grp-collapse grp-closed', ),
                                      'fields': ('sites', 'families', ), }),
        )
    raw_id_fields = ('families', 'sites', )
    autocomplete_lookup_fields = {'m2m': ['sites', 'families', ], }
    list_display = ('__str__', 'show_families', )
    search_fields = ('title', 'start_date', 'end_date', )

    def show_families(self, obj):
        return ', '.join([f.handle for f in obj.families.all()]) or '-'
    show_families.short_description = 'Eingeschränkt auf'

    class Media:
        css = {'all': ('css/timelineitem_admin.css', ) + CODEMIRROR_CSS, }
        js = CODEMIRROR_JS + (
              'js/adminactions.js', )

        try:
            js += settings.NOTARO_SETTINGS['autocomplete_helper']
        except:
            pass
        js += ('codemirror-custom/codemirror_conf_tlitem.js', )


admin.site.register(TimelineItem, TimelineItemAdmin)
