# -*- coding: utf8 -*-

"""The models of the genealogio app."""

from datetime import datetime

from django.contrib.gis.db import models
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.safestring import mark_safe
from partialdate.fields import PartialDateField

from notaro.managers import GenManager

from maps.models import Place, cleanname
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

    sites = models.ManyToManyField(Site)
    all_objects = GenManager()
    objects = CurrentSiteManager()

    date_added = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("id__iexact", "handle__icontains", )

    def related_label(self):
        if Site.objects.get_current() in self.sites.all():
            return self.__str__()
        else:
            return '[[ %s ]]' % self.__str__()

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__,
                           self.handle)

    def on_current_site(self):
        return Site.objects.get_current() in self.sites.all()

    def get_absolute_url(self):
        """Return URL where this object can be viewed."""

        return reverse('%s-detail' % self.__class__.__name__.lower(),
                       kwargs={'pk':  self.id, })


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
    TITLE_PRE = 9
    TITLE_SUFF = 10
    VULGO = 11

    NAME_TYPE = ((UNKNOWN, 'unbekannt'),
                 (OTHER, 'andere'),
                 (BIRTHNAME, 'Geburtsname'),
                 (MARRIEDNAME, 'Ehename'),
                 (TAKEN, 'Angenommener Name'),
                 (FIRSTNAME, 'Vorname'),
                 (RUFNAME, 'Rufname'),
                 (NICKNAME, 'Spitzname'),
                 (PSEUDONYM, 'Pseudonym'),
                 (FAMILYNAME, 'Familienname'),
                 (TITLE_PRE, 'Titel (vorangest.)'),
                 (TITLE_SUFF, 'Titel (nachgest.)'),
                 (VULGO, 'genannt'),
                 )

    name = models.CharField(max_length=200)
    typ = models.IntegerField(choices=NAME_TYPE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position', ]
        verbose_name = 'Name'
        verbose_name_plural = 'Namen'


class FamilyNote(models.Model):
    family = models.ForeignKey('Family', on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    position = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Text zu Familie'
        verbose_name_plural = 'Texte zu Familie'


class FamilySource(models.Model):
    family = models.ForeignKey(
            'Family',
            verbose_name="Familie",
            on_delete=models.CASCADE)
    source = models.ForeignKey(
            Source,
            verbose_name="Quelle",
            on_delete=models.CASCADE)
    comment = models.CharField(
            max_length=500,
            blank=True,
            verbose_name="Kommentar")
    position = models.IntegerField(default=1)

    class Meta:
        ordering = ('position', )


class Family(PrimaryObject):
    """The Family class, which models Father-Mother-Child relationships."""

    UNKNOWN = 0
    OTHER = 1
    MARRIED = 2
    UNMARRIED = 3
    CIVILUNION = 4
    DIVORCED = 5
    SEPARATED = 6

    FAMILY_REL_TYPE = ((UNKNOWN, 'Unbekannt'),
                       (OTHER, 'Andere'),
                       (MARRIED, 'Verheiratet'),
                       (UNMARRIED, 'Unverheiratet'),
                       (CIVILUNION, 'Eingetragene Partnerschaft'),
                       (DIVORCED, 'Geschieden'),
                       (SEPARATED, 'Getrennt lebend'),
                       )

    father = models.ForeignKey('Person', related_name="father_ref",
                               null=True, blank=True,
                               verbose_name='Vater',
                               on_delete=models.CASCADE)
    mother = models.ForeignKey('Person', related_name="mother_ref",
                               null=True, blank=True,
                               verbose_name='Mutter',
                               on_delete=models.CASCADE)
    family_rel_type = models.IntegerField(choices=FAMILY_REL_TYPE,
                                          default=3,
                                          verbose_name="Art der Beziehung")

    name = models.CharField(verbose_name='Familienname', max_length=200,
                            blank=True, null=True)
    comments = models.TextField(blank=True, verbose_name="Kommentar")

    notes = models.ManyToManyField(Note, blank=True, through=FamilyNote)
    events = models.ManyToManyField('Event', through="FamilyEvent", blank=True)
    start_date = PartialDateField(
            blank=True, default='',
            verbose_name="Anfangsdatum",
            help_text="Datum im Format JJJJ-MM-TT (Teilangaben möglich)")
    end_date = PartialDateField(
            blank=True, default='', verbose_name="Enddatum",
            help_text="Datum im Format JJJJ-MM-TT (Teilangaben möglich)")
    sources = models.ManyToManyField(Source, blank=True,
                                     verbose_name="Quellen",
                                     through=FamilySource)

    def save(self, *args, **kwargs):
        """Create handle before saving Family instance."""

        if not self.handle:
            self.handle = 'F_'

            # pylint: disable=no-member
            try:
                self.handle += cleanname(self.father.last_name)
                if self.father.datebirth:
                    self.handle += str(self.father.datebirth.year)
            except:
                pass
            try:
                self.handle += cleanname(self.mother.last_name)
                if self.mother.datebirth:
                    self.handle += str(self.mother.datebirth.year)
            except:
                pass
            self.handle = u'%s_%s' % (
                         self.handle[:44],
                         str(datetime.now().microsecond)[:5])

        # pylint: disable=no-member
        super(Family, self).save(*args, **kwargs)

    def get_children(self):
        return self.person_set(manager='objects').all().order_by('datebirth')

    def get_children_as_personfamily(self):
        return self.personfamily_set.filter(
                person__sites=Site.objects.get_current()
                ).order_by('person__datebirth')

    def get_grandchildren(self):
        qslist = []
        for c in self.get_children():
            qslist.extend([v for _k, v, _f in c.get_children()
                           if v.exists()])
        if not qslist:
            return
        qs = qslist[0]
        for x in qslist[1:]:
            qs |= x
        return qs.distinct().order_by('datebirth')

    def reset_handle(self):
        """Recompute handle for a Family object which already has an id."""

        self.handle = 'F_'

        # pylint: disable=no-member
        try:
            self.handle += cleanname(self.father.last_name)
            if self.father.datebirth:
                self.handle += str(self.father.datebirth.year)
        except:
            pass
        try:
            self.handle += cleanname(self.mother.last_name)
            if self.mother.datebirth:
                self.handle += str(self.mother.datebirth.year)
        except:
            pass

        self.handle += '-' + str(self.id)
        self.handle = self.handle[:49]
        self.save()

    def as_tag(self):
        if self.name:
            tag = self.name
        else:
            try:
                # pylint: disable=no-member
                tag = self.father.last_name
            except:
                tag = ''

        details = [tag]
        if self.start_date:
            # pylint: disable=no-member
            details.append('(%s-)' % self.start_date.year)

        # pylint: disable=no-member
        if self.father:
            details.append(self.father.get_short_name())
        if self.mother:
            details.append(self.mother.get_short_name())

        return ("Familie %s" % tag, "Familie %s" % ', '.join(details))

    def get_relation_text(self):
        texts = {
                Family.MARRIED: 'Verheiratet mit',
                Family.UNMARRIED: 'Partnerschaft mit',
                Family.DIVORCED: 'Geschieden von',
                Family.SEPARATED: 'Getrennt lebend von',
                Family.CIVILUNION: 'Eingetragene Partnerschaft mit',
                }
        return texts.get(self.family_rel_type, 'Familie mit')

    def __str__(self):
        n = ''

        # pylint: disable=no-member
        if self.name:
            n += self.name
        try:
            f = '%s %s' % (self.father.first_name, self.father.last_name)
        except AttributeError:
            f = '?'
        try:
            m = '%s %s' % (self.mother.first_name, self.mother.last_name)
        except AttributeError:
            m = '?'
        if n:
            if f != '?' and m != '?':
                n = "%s (%s und %s)" % (n, f, m)
        elif (f != '?' or m != '?'):
            n = "%s und %s" % (f, m)
        if n:
            return n
        return self.handle

    class Meta:
        ordering = ('name', 'start_date', 'id', )
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

    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    place = models.ForeignKey(
            Place,
            verbose_name='Ort', on_delete=models.CASCADE)
    start = PartialDateField(
            blank=True, default='', verbose_name='Beginn',
            help_text="Datum im Format JJJJ-MM-TT (Teilangaben möglich)")
    end = PartialDateField(
            blank=True, default='', verbose_name='Ende',
            help_text="Datum im Format JJJJ-MM-TT (Teilangaben möglich)")
    typ = models.IntegerField(choices=PP_TYPE, default=OTHER)
    comment = models.CharField(max_length=500, blank=True, default='',
                               verbose_name='Kommentar')

    def save(self, *args, **kwargs):
        # pylint: disable=no-member
        if self.typ == PersonPlace.BIRTH and\
                not self.start and self.person.datebirth:
            self.start = self.person.datebirth
        if self.typ == PersonPlace.DEATH and\
                not self.start and self.person.datedeath:
            self.start = self.person.datedeath
        super(PersonPlace, self).save(*args, **kwargs)

    def __str__(self):
        # pylint: disable=no-member
        return '%s: %s' % (self.get_typ_display(), self.place.__str__())

    class Meta:
        ordering = ['start', ]
        verbose_name = 'Zugeordneter Ort'
        verbose_name_plural = 'Zugeordnete Orte'


class PersonNote(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    position = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Text zu Person'
        verbose_name_plural = 'Texte zu Person'


class PersonSource(models.Model):
    person = models.ForeignKey(
            'Person',
            verbose_name="Person", on_delete=models.CASCADE)
    source = models.ForeignKey(
            Source,
            verbose_name="Quelle", on_delete=models.CASCADE)
    comment = models.CharField(
            max_length=500,
            blank=True,
            verbose_name="Kommentar")
    position = models.IntegerField(default=1)

    class Meta:
        ordering = ('position', )


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

    # these fields are set in the admin

    # last_name is the family name *at birth*
    last_name = models.CharField(
            max_length=200, blank=True, default='',
            verbose_name="Geburtsname")
    first_name = models.CharField(
            max_length=200, blank=True, default='',
            verbose_name="Vorname")
    last_name_current = models.CharField(
            max_length=200, blank=True, default='',
            verbose_name="Aktueller Nachname")

    gender_type = models.IntegerField('Geschlecht', choices=GENDER_TYPE,
                                      default=3)
    probably_alive = models.BooleanField("Lebt wahrscheinlich noch",
                                         default=False)
    comments = models.TextField(blank=True, verbose_name="Kommentar")

    events = models.ManyToManyField('Event', through="PersonEvent", blank=True,
                                    verbose_name="Ereignisse")

    datebirth = PartialDateField(
            "Geburtsdatum", blank=True, default='',
            help_text="Datum im Format JJJJ-MM-TT (Teilangaben möglich)")
    datedeath = PartialDateField(
            "Todesdatum", blank=True, default='',
            help_text="Datum im Format JJJJ-MM-TT (Teilangaben möglich)")

    places = models.ManyToManyField(Place, blank=True, through=PersonPlace,
                                    verbose_name='Orte')
    portrait = models.ForeignKey(Picture, blank=True, null=True,
                                 verbose_name='Portrait',
                                 on_delete=models.CASCADE)

    notes = models.ManyToManyField(Note, blank=True, through=PersonNote)
    family = models.ManyToManyField(Family, through="PersonFamily",
                                    verbose_name='Familie(n)')
    sources = models.ManyToManyField(Source, blank=True,
                                     through=PersonSource,
                                     verbose_name='Quellen')

    @property
    def year_of_birth(self):
        try:
            # pylint: disable=no-member
            return self.datebirth.year
        except:
            return ''

    @property
    def year_of_death(self):
        try:
            # pylint: disable=no-member
            return self.datedeath.year
        except:
            return ''

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

    def ancestors(self):
        result = set()
        for f in self.family.all():
            # QUESTION: should we limit this to child_type==BIRTH? FIXME
            if f.father:
                result.add(f.father)
                result |= f.father.ancestors()
            if f.mother:
                result.add(f.mother)
                result |= f.mother.ancestors()

        return result

    def descendants(self):
        result = set()
        for children in [set(x[1]) for x in self.get_children()]:
            result |= children
            for child in children:
                result |= child.descendants()

        return result

    def get_last_name(self, separator=''):
        """Return the last name."""

        if self.last_name != self.last_name_current:
            return '%s %s(geb. %s)' % (
                    self.last_name_current, separator, self.last_name)
        else:
            return '%s' % (self.last_name, )

    def get_full_name_html(self):
        return mark_safe(self.get_full_name(fmt="html"))

    def get_full_name(self, fmt="rst"):
        """Return the full name information of the person:
        - title (prefix)
        - the first name,
          if fmt is "rst" (the default):
              with the Rufname underlined (ReST-formatted)
          if fmt is "html":
              with the Rufname underlined (HTML-formatted)
          if fmt if "gedcom":
              with the surname in slashes
        - the nickname (if available), in parentheses
        - the last name (birthname or marriedname + birthname)
        - title (suffix)
        - vulgo
        """

        name = self.first_name
        template_rufname = '%s'
        lastname = '%s' % self.get_last_name()

        if fmt == "rst":
            template_rufname = ':underline:`%s`'
        elif fmt == "html":
            template_rufname =\
                    '<span style="text-decoration :underline;">%s</span>'
        elif fmt == "gedcom":
            lastname = '/%s/' % self.last_name
        else:
            template_rufname = '_%s_'

        try:
            rufname = self.name_set.filter(typ=Name.RUFNAME)[0].name
            name = name.replace(
                    rufname,
                    template_rufname % rufname)
        except IndexError:
            pass

        try:
            if name:
                name += ' (%s)'\
                        % self.name_set.filter(typ=Name.NICKNAME)[0].name
            else:
                name = '%s' % self.name_set.filter(typ=Name.NICKNAME)[0].name
        except IndexError:
            pass

        if name:
            name += ' ' + lastname
        else:
            name = lastname

        try:
            name = '%s %s' % (
                    self.name_set.filter(typ=Name.TITLE_PRE)[0].name, name)
        except IndexError:
            pass

        try:
            name = '%s %s' % (
                    name, self.name_set.filter(typ=Name.TITLE_SUFF)[0].name)
        except IndexError:
            pass

        try:
            name = '%s, genannt %s' % (
                    name, self.name_set.filter(typ=Name.VULGO)[0].name)
        except IndexError:
            pass

        # FIXME: incorporate further names (other types + several names
        # of the same type)

        return name.strip()

    def get_short_name(self):
        """
        Return a "short" name of the person, to be used in pedigrees and
        descendant trees.
        """

        first = ''
        try:
            first = self.name_set.filter(typ=Name.NICKNAME)[0].name
        except IndexError:
            pass

        if not first:
            try:
                first = self.name_set.filter(typ=Name.RUFNAME)[0].name
            except IndexError:
                pass

        if not first:
            first = self.first_name

        name = self.last_name

        if len(first) + len(name) > 22:
            fsplit = first.split(' ')
            first = ' '.join(fsplit[:1] + [x[0]+'.' for x in fsplit[1:]])
        if len(first) + len(name) > 22:
            first = first[0] + '.'
        return ('%s %s' % (first, name)).strip()

    def get_primary_name(self):
        """
        Return the preferred name of a person.
        """

        return ('%s %s' % (self.first_name, self.get_last_name())).strip()

    def get_primary_name_br(self):
        """
        Return the preferred name of a person.
        """

        n = '%s %s' % (self.first_name,
                       self.get_last_name(separator='|br| '))
        return n.strip()

    def get_father(self):
        try:
            # FIXME should be more careful here if several families exist
            father = self.family.filter(
                    sites=Site.objects.get_current())[0].father
            if Site.objects.get_current() in father.sites.all():
                return father
        except (AttributeError, IndexError):
            pass

    def get_mother(self):
        try:
            # FIXME should be more careful here if several families exist
            mother = self.family.filter(
                    sites=Site.objects.get_current())[0].mother
            if Site.objects.get_current() in mother.sites.all():
                return mother
        except (AttributeError, IndexError):
            pass

    def get_children(self):
        """
        Get all children of this person (as stored in the Family objects
        attached to it via the family m2m.

        Returns a list of tuples, one tuple for each family which gave rise to
        children of self, each tuple consisting of
        - other parent of the family
        - queryset of children of that family
        - Family object
        """

        # pylint: disable=no-member
        children = []
        for fam in Family.objects.filter(
                father=self,
                sites=Site.objects.get_current()).order_by('start_date'):
            m = fam.mother
            children.append([
                m,
                fam.person_set(manager='objects').all().order_by(
                    'datebirth', 'handle'),
                fam
                ])
        for fam in Family.objects.filter(
                mother=self,
                sites=Site.objects.get_current()).order_by('start_date'):
            f = fam.father
            children.append([
                f,
                fam.person_set(manager='objects').all().order_by(
                    'datebirth', 'handle'),
                fam
                ])
        return children

    @property
    def has_spouse(self):
        # pylint: disable=no-member
        if Family.objects.filter(father=self).exists():
            return True
        if Family.objects.filter(mother=self).exists():
            return True
        return False

    @staticmethod
    def get_handle(**kwargs):
        """
        kwargs may include (otherwise the default value specified below will be
        used):
            last_name='',
            first_name='',
            married_name='',
            datebirth=None,
            datedeath=None,
            id=None            # if available, will be used as final part,
                                 otherwise, append "random" number

        Other items contained in kwargs will be ignored.
        """

        handle = 'P_'
        handle += cleanname(kwargs.get('last_name', ''))[:20]
        handle += cleanname(kwargs.get('married_name', ''))[:20]
        handle += cleanname(kwargs.get('first_name', ''))[:20]

        try:
            handle += str(kwargs['datebirth'].year)
        except:
            pass
        try:
            handle += str(kwargs['datedeath'].year)
        except:
            pass
        handle = handle[:44]

        if 'id' in kwargs:
            handle += '-' + str(kwargs['id'])
        else:
            handle += u'_' + str(datetime.now().microsecond)[:5]

        handle = handle[:49]
        return handle

    def reset_handle(self):
        """Recompute handle for a Person object which already has an id."""

        try:
            married_name = self.name_set.filter(typ=Name.MARRIEDNAME)[0].name
        except IndexError:
            married_name = ''
        self.handle = Person.get_handle(
                last_name=self.last_name,
                first_name=self.first_name,
                married_name=married_name,
                datebirth=self.datebirth,
                datedeath=self.datedeath,
                id=self.id)

        # pylint: disable=no-member
        self.save()

    def as_tag(self):
        tag = self.get_short_name()
        details = self.get_primary_name()
        if self.year_of_birth or self.year_of_death:
            details += ' (%s~%s)' % (self.year_of_birth, self.year_of_death)

        return ("%s" % tag, details)

    def __str__(self):
        return u"%s %s" % (self.get_primary_name(), self.handle)

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

    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    family = models.ForeignKey(
            Family,
            verbose_name='Familie', on_delete=models.CASCADE)
    child_type = models.IntegerField(choices=CHILD_REF_TYPE,
                                     default=2, verbose_name="Typ")
    position = models.PositiveIntegerField(default=1)

    def get_child_type(self):
        if self.child_type == PersonFamily.ADOPTED:
            return " (adoptiert)"
        elif self.child_type == PersonFamily.STEPCHILD:
            return " (Stiefkind)"
        elif self.child_type == PersonFamily.FOSTER:
            return " (Pflegekind)"

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

    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    event = models.ForeignKey(
            'Event',
            verbose_name='Ereignis', on_delete=models.CASCADE)
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
    family = models.ForeignKey(
            'Family',
            verbose_name='Familie', on_delete=models.CASCADE)
    event = models.ForeignKey(
            'Event',
            verbose_name='Ereignis', on_delete=models.CASCADE)
    role = models.IntegerField(choices=EVENT_ROLE_TYPE, default=-1,
                               verbose_name='Rolle')
    position = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Ereignis zu Familie'
        verbose_name_plural = 'Ereignisse zu Familie'


class EventNote(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    position = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Text zu Ereignis'
        verbose_name_plural = 'Texte zu Ereignis'


class EventSource(models.Model):
    event = models.ForeignKey(
            'Event',
            verbose_name="Ereignis", on_delete=models.CASCADE)
    source = models.ForeignKey(
            Source,
            verbose_name="Quelle", on_delete=models.CASCADE)
    comment = models.CharField(
            max_length=500,
            blank=True,
            verbose_name="Kommentar")
    position = models.IntegerField(default=1)

    class Meta:
        ordering = ('position', )


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
    date = PartialDateField(
            blank=True, default='', verbose_name='Datum',
            help_text="Datum im Format JJJJ-MM-TT (Teilangaben möglich)")
    description = models.TextField(blank=True,
                                   verbose_name='Beschreibung')
    place = models.ForeignKey(Place, null=True, blank=True,
                              verbose_name='Ort',
                              on_delete=models.CASCADE)
    sources = models.ManyToManyField(Source, blank=True,
                                     through=EventSource,
                                     verbose_name='Quellen')
    notes = models.ManyToManyField(Note, blank=True, through=EventNote)

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("id__iexact", "title__icontains", "handle__icontains", )

    def reset_handle(self):
        """Recompute handle for a Event object which already has an id."""

        self.handle = 'E_'
        self.handle += cleanname(self.title)[:20]

        # pylint: disable=no-member
        if self.date:
            self.handle += str(self.date.year)
        if self.place:
            self.handle += cleanname(self.place.title)[:20]

        self.handle += '-' + str(self.id)
        self.handle = self.handle[:49]
        self.save()

    def as_tag(self):
        return (self.title, self.title)

    def __str__(self):
        return "%s (%s)" % (self.title, self.get_event_type_display())

    def description_indented(self):
        return '    ' + '\n    '.join(self.description.splitlines()) + '\n'

    class Meta:
        ordering = ('date', 'event_type', )
        verbose_name = 'Ereignis'
        verbose_name_plural = 'Ereignisse'


class TimelineItem(models.Model):

    OTHER = 1
    WAR = 2
    INVENTION = 3
    POLITICAL_EVENT = 4
    ECONOMIC_EVENT = 5
    CRISIS = 6
    REVOLUTION = 7
    OTHER_BLUE = 8
    OTHER_GREEN = 9
    OTHER_GRAY = 10

    TYPE_CHOICES = (
            (OTHER, 'Anderes Ereignis'),
            (WAR, 'Krieg'),
            (INVENTION, 'Erfindung'),
            (POLITICAL_EVENT, 'Politisches Ereignis'),
            (ECONOMIC_EVENT, 'Wirtschaftliches Ereignis'),
            (CRISIS, 'Krisenzeit'),
            (REVOLUTION, 'Umsturz, Revolution'),
            (OTHER_BLUE, 'Anderes Ereignis (blau)'),
            (OTHER_GREEN, 'Anderes Ereignis (grün)'),
            (OTHER_GRAY, 'Anderes Ereignis (grau)'),
            )

    COLORS = {
            OTHER: [0, 0, 0],                # black
            WAR: [1, 0, 0],                  # red
            INVENTION: [1, 0, 1],            # magenta
            POLITICAL_EVENT: [0, 0, 0.5],    # navy
            ECONOMIC_EVENT: [0.5, 0.5, 0],   # olive
            CRISIS: [1, 0.5, 0],             # orange
            REVOLUTION: [0.9, 0.1, 0.2],     # crimson
            OTHER_BLUE: [0, 0, 1],           # blue
            OTHER_GREEN: [0, 1, 0],          # green (lime)
            OTHER_GRAY: [0.3, 0.3, 0.3],     # gray
            }

    title = models.CharField(max_length=200, verbose_name='Titel')
    url = models.CharField(max_length=200, verbose_name='URL',
                           blank=True)
    start_date = PartialDateField(
            verbose_name='Startdatum', blank=True, default='',
            help_text="Datum im Format JJJJ-MM-TT (Teilangaben möglich)")
    end_date = PartialDateField(
            blank=True, default='',
            verbose_name='Enddatum',
            help_text="Datum im Format JJJJ-MM-TT (Teilangaben möglich); "
                      "kann freibleiben"
            )
    description = models.TextField(
            blank=True, default='',
            verbose_name="Beschreibung",
            help_text="Wird beim pdf-Export verwendet, kann als ReST "
                      "formattiert werden, mit Links auf Objekte der "
                      "Datenbank (siehe Dokumentation).")
    typ = models.IntegerField(choices=TYPE_CHOICES,
                              verbose_name="Art des Ereignisses")

    sites = models.ManyToManyField(Site)
    families = models.ManyToManyField(
            Family,
            blank=True,
            verbose_name="Familien",
            help_text="Sind hier Familien ausgewählt, so wird der Eintrag "
                      "nur bei den ausgewählten Familien angezeigt, "
                      "sonst bei allen Familien")

    all_objects = GenManager()
    objects = CurrentSiteManager()

    @property
    def start(self):
        # pylint: disable=no-member
        return self.start_date.year

    @property
    def end(self):
        # pylint: disable=no-member
        if self.end_date:
            return self.end_date.year
        else:
            return self.start_date.year

    @property
    def period(self):
        return '%s-%s' % (self.start, self.end) if self.end_date\
               else str(self.start)

    @property
    def color(self):
        return self.COLORS[self.typ]

    def __str__(self):
        return '%s (%s)' % (self.title, self.period)

    class Meta:
        ordering = ('start_date', 'end_date', 'title', )
        verbose_name = 'Ereignis im Zeitstrahl'
        verbose_name_plural = 'Ereignisse im Zeitstrahl'

