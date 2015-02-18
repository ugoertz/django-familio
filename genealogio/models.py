# -*- coding: utf8 -*-

"""The models of the genealogio app."""


from __future__ import unicode_literals

from collections import OrderedDict

from django.contrib.gis.db import models
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from partialdate.fields import PartialDateField
from notaro.models import Source, Note, Picture


class PrimaryObject(models.Model):
    """An abstract base class for several kinds of objects.

    Provides a handle, notes, source, and association with sites.
    """

    class Meta:
        abstract = True

    handle = models.CharField(max_length=50, unique=True)

    private = models.BooleanField('private', default=False)
    public = models.BooleanField('public', default=False)

    notes = models.ManyToManyField(Note, blank=True)

    sites = models.ManyToManyField(Site)
    date_added = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s: %s" % (self.__class__.__name__,
                            self.handle)

    def get_absolute_url(self):
        """Return URL where this object can be viewed (using handle)."""

        return reverse('%s-detail' % self.__class__.__name__.lower(),
                       kwargs={'pk':  self.id, })


class Url(models.Model):
    title = models.CharField(max_length=200, blank=True)
    link = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title or self.link[:50]

    def related_label(self):
        return '<a href="%s">%s</a>' %\
               (self.link, self.title or self.link[:50], )


class PlaceUrl(models.Model):
    url = models.ForeignKey(Url)
    place = models.ForeignKey('Place')
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ('position', )
        verbose_name = 'URL zum Ort'
        verbose_name_plural = 'URLs zum Ort'


class Place(PrimaryObject):
    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(blank=True)

    urls = models.ManyToManyField(Url, through=PlaceUrl, blank=True)
    location = models.PointField(blank=True, null=True)

    objects = models.GeoManager()

    def born_here(self):
        # pylint: disable=no-member
        return Person.objects.filter(personplace__place=self.id,
                                     personplace__typ=PersonPlace.BIRTH)

    def died_here(self):
        # pylint: disable=no-member
        return Person.objects.filter(personplace__place=self.id,
                                     personplace__typ=PersonPlace.DEATH)

    def events_here(self):
        # pylint: disable=no-member
        return Event.objects.filter(place=self)

    def __unicode__(self):
        return self.title

    @staticmethod
    def autocomplete_search_fields():
        return ("title__startswith",)

    class Meta:
        ordering = ('title', )
        verbose_name = 'Ort'
        verbose_name_plural = 'Orte'


class Name(models.Model):
    UNKNOWN = -1
    OTHER = 0
    BIRTHNAME = 1
    MARRIEDNAME = 2
    TAKEN = 3
    FIRSTNAME = 4
    RUFNAME = 5
    NICKNAME = 6
    PSEUDONYM = 7
    FAMILYNAME = 8

    NAME_TYPE = ((UNKNOWN, 'unbekannt'),
                 (OTHER, 'andere'),
                 (BIRTHNAME, 'Geburtsname'),
                 (MARRIEDNAME, 'Ehename'),
                 (TAKEN, 'Angenommener Name'),
                 (FIRSTNAME, 'Vorname'),
                 (RUFNAME, 'Rufname'),
                 (NICKNAME, 'Spitzname'),
                 (PSEUDONYM, 'Pseudonym'),
                 (FAMILYNAME, 'Familienname'), )

    name = models.CharField(max_length=200)
    typ = models.IntegerField(choices=NAME_TYPE)
    person = models.ForeignKey('Person')
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position', ]
        verbose_name = 'Name'
        verbose_name_plural = 'Namen'


class Family(PrimaryObject):
    """The Family class, which models Father-Mother-Child relationships."""

    UNKNOWN = 0
    OTHER = 1
    MARRIED = 2
    UNMARRIED = 3
    CIVILUNION = 4

    FAMILY_REL_TYPE = ((UNKNOWN, 'Unbekannt'),
                       (OTHER, 'Andere'),
                       (MARRIED, 'Verheiratet'),
                       (UNMARRIED, 'Unverheiratet'),
                       (CIVILUNION, 'Eingetragene Partnerschaft'), )

    father = models.ForeignKey('Person', related_name="father_ref",
                               null=True, blank=True)
    mother = models.ForeignKey('Person', related_name="mother_ref",
                               null=True, blank=True)
    family_rel_type = models.IntegerField('FamilyRelType',
                                          choices=FAMILY_REL_TYPE, default=3)

    name = models.ManyToManyField('Name', blank=True, null=True)

    events = models.ManyToManyField('Event', through="FamilyEvent", blank=True)
    start_date = PartialDateField(blank=True, null=True)
    end_date = PartialDateField(blank=True, null=True)
    source = models.ManyToManyField(Source, blank=True)

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("id__iexact", "handle__icontains", )

    def __unicode__(self):
        # pylint: disable=no-member
        qs = self.name.filter(typ=Name.FAMILYNAME)
        if qs.count():
            return qs[0].name
        elif self.father and self.mother:
            return u"%s und %s" % (self.father.get_primary_name(),
                                   self.mother.get_primary_name(), )
        else:
            return self.handle

    class Meta:
        verbose_name = 'Familie'
        verbose_name_plural = 'Familien'


class PersonPlace(models.Model):

    UNKNOWN = 0
    OTHER = 1
    BIRTH = 2
    DEATH = 3
    CHILDHOOD = 4
    STUDIES = 5
    RETIREMENT = 6
    BURIAL = 7

    PP_TYPE = ((UNKNOWN, 'Unbekannt'),
               (OTHER, 'Anderer'),
               (BIRTH, 'Geburt'),
               (DEATH, 'Tod'),
               (CHILDHOOD, 'Kindheit'),
               (STUDIES, 'Ausbildung/Studium'),
               (RETIREMENT, 'Ruhestand'),
               (BURIAL, 'Grabstätte'),
               )

    person = models.ForeignKey('Person')
    place = models.ForeignKey('Place')
    start = PartialDateField(blank=True, null=True)
    end = PartialDateField(blank=True, null=True)
    typ = models.IntegerField(choices=PP_TYPE)
    comment = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        ordering = ['start', ]
        verbose_name = 'Zugeordneter Ort'
        verbose_name_plural = 'Zugeordnete Orte'


class Person(PrimaryObject):
    """The Person class."""

    UNKNOWN = 3
    OTHER = 2
    MALE = 1
    FEMALE = 0

    GENDER_TYPE = ((UNKNOWN, 'unbekannt'),
                   (OTHER, 'anderes'),
                   (MALE, 'männlich'),
                   (FEMALE, 'weiblich'), )

    last_name = models.CharField(max_length=200, blank=True, default='')
    first_name = models.CharField(max_length=200, blank=True, default='')

    gender_type = models.IntegerField('Geschlecht', choices=GENDER_TYPE,
                                      default=3)
    probably_alive = models.BooleanField("Lebt wahrscheinlich noch",
                                         default=False)
    comments = models.TextField(blank=True, verbose_name="Kommentar")

    events = models.ManyToManyField('Event', through="PersonEvent", blank=True,
                                    verbose_name="Ereignisse")

    datebirth = PartialDateField("Geburtsdatum", blank=True, null=True)
    datedeath = PartialDateField("Todesdatum", blank=True, null=True)

    places = models.ManyToManyField(Place, blank=True, through=PersonPlace,
                                    verbose_name='Orte')
    portrait = models.ForeignKey(Picture, blank=True, null=True,
                                 verbose_name='Portrait')

    family = models.ManyToManyField(Family, through="PersonFamily",
                                    verbose_name='Familie(n)')
    source = models.ManyToManyField(Source, blank=True,
                                    verbose_name='Quelle')

    objects = models.GeoManager()

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("id__iexact", "handle__icontains", )

    @property
    def placebirth(self):
        try:
            return self.places.get(personplace__typ=PersonPlace.BIRTH)
        except:
            return

    @property
    def placedeath(self):
        try:
            return self.places.get(personplace__typ=PersonPlace.DEATH)
        except:
            return

    def get_primary_name(self):
        """
        Return the preferred name of a person.
        """

        firstname = ''
        try:
            firstname = self.name_set.filter(typ=Name.FIRSTNAME)[0].name
        except:
            pass

        birthname = ''
        try:
            birthname = self.name_set.filter(typ=Name.BIRTHNAME)[0].name
        except:
            pass

        marriedname = ''
        try:
            marriedname = self.name_set.filter(typ=Name.MARRIEDNAME)[0].name
        except:
            pass

        if marriedname:
            return '%s %s (geb. %s)' % (firstname, marriedname, birthname)
        else:
            return '%s %s' % (firstname, birthname)

    def get_father(self):
        try:
            # FIXME should be more careful here if several families exist
            return self.family.all()[0].father
        except IndexError:
            return None

    def get_mother(self):
        try:
            # FIXME should be more careful here if several families exist
            return self.family.all()[0].mother
        except IndexError:
            return None

    def get_children(self):
        """Get all children of this person (as stored in the Family objects
        attached to it via the family m2m."""

        children = OrderedDict()
        for fam in Family.objects.filter(father=self):
            children[fam.mother] =\
                fam.person_set.all().order_by('datebirth', 'handle')
        for fam in Family.objects.filter(mother=self):
            children[fam.father] =\
                fam.person_set.all().order_by('datebirth', 'handle')
        return children

    def __unicode__(self):
        return u"(%s [%s])" % (self.get_primary_name(), self.handle)

    # def get_selection_string(self):
    #     return self.name_set.get(preferred=True).get_selection_string()

    class Meta:
        ordering = ('handle', 'datebirth', )
        verbose_name = 'Person'
        verbose_name_plural = 'Personen'


class PersonFamily(models.Model):
    """Through model for Person-Family m2m relationship."""

    UNKNOWN = 0
    OTHER = 1
    BIRTH = 2
    ADOPTED = 3
    STEPCHILD = 4
    FOSTER = 5

    CHILD_REF_TYPE = ((UNKNOWN, 'unbekannt'),
                      (OTHER, 'anderer'),
                      (BIRTH, 'Geburt'),
                      (ADOPTED, 'Adoption'),
                      (STEPCHILD, 'Stiefkind'),
                      (FOSTER, 'Pflegekind'), )

    person = models.ForeignKey(Person)
    family = models.ForeignKey(Family, verbose_name='Familie')
    child_type = models.IntegerField(choices=CHILD_REF_TYPE,
                                     default=2, verbose_name="Typ")
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['position', ]
        verbose_name = 'Person-Familie-Beziehung'
        verbose_name_plural = 'Person-Familie-Beziehungen'


class PersonEvent(models.Model):
    """Through class for Person-Event m2m relationship."""

    UNKNOWN = -1
    OTHER = 1
    PRIMARY = 2
    GODPARENT = 3
    BRIDE = 4
    GROOM = 5
    WITNESS = 6
    FAMILY = 7

    EVENT_ROLE_TYPE = ((UNKNOWN, 'unbekannt'),
                       (OTHER, 'andere'),
                       (PRIMARY, 'Hauptperson'),
                       (GODPARENT, 'Pate/Patin'),
                       (BRIDE, 'Braut'),
                       (GROOM, 'Bräutigam'),
                       (WITNESS, 'Trauzeuge'),
                       (FAMILY, 'Familienmitglied'), )

    person = models.ForeignKey('Person')
    event = models.ForeignKey('Event', verbose_name='Ereignis')
    role = models.IntegerField(choices=EVENT_ROLE_TYPE, default=-1,
                               verbose_name='Rolle')

    class Meta:
        ordering = ('role', )
        verbose_name = 'Ereignis zu Person'
        verbose_name_plural = 'Ereignisse zu Person'


class FamilyEvent(models.Model):
    UNKNOWN = 0
    OTHER = 1
    PRIMARY = 2
    FAMILY = 7

    EVENT_ROLE_TYPE = ((UNKNOWN, 'unbekannt'),
                       (OTHER, 'andere'),
                       (PRIMARY, 'Hauptperson'),
                       (FAMILY, 'Familienmitglied'), )
    family = models.ForeignKey('Family', verbose_name='Familie')
    event = models.ForeignKey('Event', verbose_name='Ereignis')
    role = models.IntegerField(choices=EVENT_ROLE_TYPE, default=-1,
                               verbose_name='Rolle')
    position = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Ereignis zu Familie'
        verbose_name_plural = 'Ereignisse zu Familie'


class Event(PrimaryObject):
    BIRTH = 20
    ADOPTED = 30
    DEATH = 40
    RELIGION = 50
    BAPTISM = 60
    ENGAGEMENT = 70
    MARRIAGE = 80
    MARRIAGECHURCH = 90
    ALTERNATEMARRIAGE = 100
    DIVORCE = 110
    EDUCATION = 120
    OCCUPATION = 130
    SPORTS = 140
    BURIAL = 150
    CAUSEOFDEATH = 160
    OTHER = 990
    UNKNOWN = 1000

    EVENT_TYPE = ((UNKNOWN, 'Unbekanntes Ereignis'),
                  (OTHER, 'Anderes Ereignis'),
                  (MARRIAGE, 'Standesamtliche Hochzeit'),
                  (MARRIAGECHURCH, 'Kirchliche Hochzeit'),
                  (ENGAGEMENT, 'Verlobung'),
                  (DIVORCE, 'Scheidung'),
                  (ALTERNATEMARRIAGE, 'Verpartnerung'),
                  (ADOPTED, 'Adoption'),
                  (BIRTH, 'Geburt'),
                  (DEATH, 'Tod'),
                  (BAPTISM, 'Taufe'),
                  (BURIAL, 'Bestattung'),
                  (CAUSEOFDEATH, 'Todesursache'),
                  (EDUCATION, 'Ausbildung'),
                  (OCCUPATION, 'Beruf'),
                  (SPORTS, 'Sport'),
                  (RELIGION, 'Religion'), )

    event_type = models.IntegerField(choices=EVENT_TYPE,
                                     verbose_name='Typ')
    title = models.CharField(max_length=200, verbose_name='Titel')
    date = PartialDateField(blank=True, null=True, verbose_name='Datum')
    description = models.TextField(blank=True,
                                   verbose_name='Beschreibung')
    place = models.ForeignKey('Place', null=True, blank=True,
                              verbose_name='Ort')
    source = models.ManyToManyField(Source, blank=True,
                                    verbose_name='Quelle')

    objects = models.GeoManager()

#    references = generic.GenericRelation('EventRef', related_name="refs",
#                                         content_type_field="object_type",
#                                         object_id_field="object_id")

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("id__iexact", "title__icontains", "handle__icontains", )

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.get_event_type_display())

    class Meta:
        ordering = ('event_type', )
        verbose_name = 'Ereignis'
        verbose_name_plural = 'Ereignisse'