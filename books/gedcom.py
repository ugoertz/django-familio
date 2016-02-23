# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import division

import datetime
from collections import OrderedDict
from functools import wraps
from itertools import chain

from django.contrib.sites.models import Site

from genealogio.models import Family, Name, Person


class Writer(object):
    """
    Abstract base class for exporting database.
    """

    def __init__(self, *args, **kwargs):
        # self.objects is an OrderedDict
        # "type_of_object":
        # {"objects": [list of objects],
        #  "funcs": [list of functions to apply when exporting this object], }
        self.objects = OrderedDict()

    def export(self):
        result = [self.write_header(), ]
        for _, o in self.objects.items():
            for obj in o['objects']:
                result.append(self.write_object(obj, o['funcs']))
        result.append(self.write_footer())
        return '\n'.join(result)

    def write_header(self):
        return ''

    def write_footer(self):
        return ''

    def write_object(self, obj, funcs):
        res = [fct(obj) for fct in funcs]
        return '\n'.join(chain(*res))


def GEDCOM_line_breaks(f):
    # introduce GEDCOM style line breaks wherever necessary
    # replace @ in text by @@ (but not in pointers)

    @wraps(f)
    def f_with_line_breaks(*args, **kwargs):
        taglist = f(*args, **kwargs)
        result = []

        for t in taglist:
            try:
                level = int(t.split(' ')[0])
            except:
                # FIXME --- handle this more explicitly
                continue

            # replace @'s
            items = t.split(' ')

            # first two items cannot contain text @'s but second item could be
            # pointer with regular @'s
            res = ' '.join(items[:2])
            if len(items) > 2:
                if items[1] in [
                        'FAMC', 'FAMS',
                        'HUSB', 'WIFE', 'CHIL',
                        'SOUR', ]:
                    res += ' ' + ' '.join(items[2:])
                else:
                    res += ' ' + ' '.join(
                            s.replace('@', '@@') for s in items[2:])

            lines = res.splitlines()
            for ctr, l in enumerate(lines):
                if not l:
                    # can happen in NOTE texts when we have empty lines
                    result.append('{l1} CONT '.format(l1=level+1))
                    continue

                chunks = [l[i:i+200] for i in range(0, len(l), 200)]
                if ctr == 0:
                    result.append(chunks[0])
                else:
                    result.append('{l1} CONT {txt}'.format(
                        l1=level+1, txt=chunks[0]))
                result.extend(
                        '{l1} CONC {txt}'.format(l1=level+1, txt=c)
                        for c in chunks[1:])

        return result

    return f_with_line_breaks


class GEDCOMWriter(Writer):

    def __init__(self, *args, **kwargs):
        super(GEDCOMWriter, self).__init__(*args, **kwargs)
        self.objects['persons'] = {
                'objects': kwargs.get('persons', []),
                'funcs': [
                    self._write_p_header,
                    self._write_p_name,
                    self._write_p_sex,
                    self._write_p_birth,
                    self._write_p_death,
                    self._write_p_in_family,
                    self._write_obj_events,
                    self._write_p_comments,
                    self._write_p_sources,
                    self._write_obj_lastchange,
                    ],
                }
        self.objects['families'] = {
                'objects': kwargs.get('families', []),
                'funcs': [
                    self._write_f_header,
                    self._write_f_persons,
                    self._write_f_events,
                    self._write_obj_events,
                    self._write_f_sources,
                    self._write_obj_lastchange,
                    ],
                }
        self.objects['notes'] = {
                'objects': kwargs.get('notes', []),
                'funcs': [
                    self._write_note,
                    self._write_n_sources,
                    self._write_obj_lastchange,
                    ],
                }

        # self.objects['sources']['objects'] if filled automatically when
        # exporting other objects; make is a set to avoid duplicates
        self.objects['sources'] = {
                'objects': set([]),
                'funcs': [self._write_source, ],
                }

        # list of events assed to init is stored here, but events are exported
        # only as part of other records
        self.events = kwargs.get('events', [])

    def write_header(self):
        s = """0 HEAD
1 CHAR UTF-8
1 DATE {date}
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 LANG German"""
        return s.format(date=self.write_date(datetime.datetime.today()))

    def write_footer(self):
        return '0 TRLR'

    def _write_source(self, obj, level=0):
        res = []
        res.append('0 @S{id}@ SOUR'.format(id=obj.id))
        res.append('1 TITL {txt}'.format(txt=obj.name))
        if obj.description:
            res.append('1 NOTE {txt}'.format(txt=obj.description))
        return res

    @staticmethod
    def write_place(pl, level):
        res = []
        res.append('{l} PLAC {pl}'.format(l=level, pl=pl.title))
        if pl.location:
            res.append('{l1} MAP'.format(l1=level+1))
            if pl.latitude >= 0:
                res.append('{l2} LATI N{l}'.format(l2=level+2, l=pl.latitude))
            else:
                res.append('{l2} LATI S{l}'.format(l2=level+2, l=-pl.latitude))
            if pl.longitude >= 0:
                res.append('{l2} LONG E{l}'.format(l2=level+2, l=pl.longitude))
            else:
                res.append('{l2} LONG W{l}'.format(l2=level+2, l=pl.longitude))
        return res

    @staticmethod
    def write_date(d):
        m = {
            1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN',
            7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC',
            }.get(d.month, '')
        if d.day:
            return '{0} {1} {2}'.format(d.day, m, d.year)
        elif m:
            return '{0} {1}'.format(m, d.year)
        return '{0}'.format(d.year)

    def _write_p_header(self, p, level=1):
        return ['0 @I{id}@ INDI'.format(id=p.id), ]

    @GEDCOM_line_breaks
    def _write_p_name(self, p, level=1):
        res = []
        res.append('{l} NAME {n}'.format(
                l=level, n=p.get_full_name(fmt="gedcom")))
        res.append('{l1} TYPE birth'.format(l1=level+1))
        if p.first_name:
            res.append('{l1} GIVN {n}'.format(l1=level+1, n=p.first_name))
        res.append('{l1} SURN {n}\n'.format(l1=level+1, n=p.last_name))
        try:
            res.append('{l1} NICK {n}'.format(
                    l1=level+1,
                    n=p.name_set.filter(typ=Name.NICKNAME)[0].name))
        except IndexError:
            pass
        try:
            res.append('{l1} NPFX {n}'.format(
                    l1=level+1,
                    n=p.name_set.filter(typ=Name.TITLE_PRE)[0].name))
        except IndexError:
            pass

        try:
            res.append('{l1} NSFX {n}'.format(
                    l1=level+1,
                    n=p.name_set.filter(typ=Name.TITLE_SUFF)[0].name))
        except IndexError:
            pass

        try:
            aka = p.name_set.filter(typ=Name.VULGO)[0].name
            res.append('{l} NAME {n}'.format(l=level, n=aka))
            res.append('{l1} TYPE aka'.format(l1=level+1))
        except IndexError:
            pass

        if p.last_name != p.last_name_current:
            res.append('{l} NAME {n}'.format(l=level, n=p.last_name_current))
            res.append('{l1} TYPE married'.format(l1=level+1))

        return res

    @GEDCOM_line_breaks
    def _write_p_sex(self, p, level=1):
        t = '{l} SEX {gt}'
        if p.gender_type == Person.FEMALE:
            return [t.format(l=level, gt='F'), ]
        if p.gender_type == Person.MALE:
            return [t.format(l=level, gt='M'), ]
        return [t.format(l=level, gt='U'), ]

    @GEDCOM_line_breaks
    def _write_p_birth(self, p, level=1):
        if not (p.datebirth or p.placebirth):
            return []

        res = ['{l} BIRT'.format(l=level), ]
        if p.datebirth:
            res.append('{l1} DATE {dt}'.format(
                    l1=level+1, dt=self.write_date(p.datebirth)))
        if p.placebirth:
            res.extend(self.write_place(p.placebirth, level+1))

        return res

    @GEDCOM_line_breaks
    def _write_p_death(self, p, level=1):
        if not (p.datedeath or p.placedeath):
            return []

        res = ['{l} DEAT'.format(l=level), ]
        if p.datedeath:
            res.append('{l1} DATE {dt}'.format(
                l1=level+1, dt=self.write_date(p.datedeath)))
        if p.placedeath:
            res.extend(self.write_place(p.placedeath, level+1))

        return res

    @GEDCOM_line_breaks
    def _write_p_in_family(self, p, level=1):
        res = []
        for fam in Family.objects.filter(
                father=p,
                sites=Site.objects.get_current()).order_by('start_date'):
            if fam not in self.objects['families']['objects']:
                continue
            res.append('{l} FAMS @F{id}@'.format(l=level, id=fam.id))

        for fam in Family.objects.filter(
                mother=p,
                sites=Site.objects.get_current()).order_by('start_date'):
            if fam not in self.objects['families']['objects']:
                continue
            res.append('{l} FAMS @F{id}@'.format(l=level, id=fam.id))

        for fam in p.family.all():
            if fam not in self.objects['families']['objects']:
                continue
            res.append('{l} FAMC @F{id}@'.format(l=level, id=fam.id))

        return res

    @GEDCOM_line_breaks
    def _write_p_comments(self, p, level=1):
        if p.comments.strip():
            return ['{l} NOTE {t}'.format(l=level, t=p.comments), ]

        return []

    @GEDCOM_line_breaks
    def _write_obj_events(self, obj, level=1):
        res = []
        for evt in obj.events.all():
            if evt not in self.events:
                continue
            res.append('{l} EVEN'.format(l=level))
            if evt.title:
                res.append('{l1} TYPE {t}'.format(l1=level+1, t=evt.title))
            if evt.date:
                res.append('{l1} DATE {dt}'.format(
                        l1=level+1, dt=self.write_date(evt.date)))
            if evt.description:
                res.append('{l1} NOTE {t}'.format(
                    l1=level+1, t=evt.description))
            if evt.place:
                res.extend(self.write_place(evt.place, level+1))

        return res

    def _write_f_header(self, f, level=1):
        return ['0 @F{id}@ FAM'.format(id=f.id), ]

    @GEDCOM_line_breaks
    def _write_f_persons(self, f, level=1):
        res = []
        if f.father and f.father in self.objects['persons']['objects']:
            res.append('{l} HUSB @I{id}@'.format(l=level, id=f.father.id))
        if f.mother and f.mother in self.objects['persons']['objects']:
            res.append('{l} WIFE @I{id}@'.format(l=level, id=f.mother.id))
        for c in f.get_children():
            if c not in self.objects['persons']['objects']:
                continue
            res.append('{l} CHIL @I{id}@'.format(l=level, id=c.id))

        return res

    def _write_obj_sources(self, sourcelist, level):
        res = []
        for src in sourcelist:
            self.objects['sources']['objects'].add(src.source)
            res.append('{l} SOUR @S{id}@'.format(l=level, id=src.source.id))
            res.append('{l1} PAGE {txt}'.format(l1=level+1, txt=src.comment))
        return res

    @GEDCOM_line_breaks
    def _write_p_sources(self, obj, level=1):
        return self._write_obj_sources(
                obj.personsource_set.all().select_related(), level)

    @GEDCOM_line_breaks
    def _write_f_sources(self, obj, level=1):
        return self._write_obj_sources(
                obj.familysource_set.all().select_related(), level)

    @GEDCOM_line_breaks
    def _write_n_sources(self, obj, level=1):
        return self._write_obj_sources(
                obj.notesource_set.all().select_related(), level)

    @GEDCOM_line_breaks
    def _write_f_events(self, f, level=1):
        res = []
        if f.family_rel_type == Family.MARRIED:
            if f.start_date:
                res.append('{l} MARR'.format(l=level))
                res.append('{l1} DATE {dt}'.format(
                    l1=level+1, dt=self.write_date(f.start_date)))
            else:
                res.append('{l} MARR Y'.format(l=level))

        return res

    @GEDCOM_line_breaks
    def _write_note(self, n, level=1):
        res = []
        res.append('0 @N{id}@ NOTE {title}\n{txt}'.format(
            l=level, id=n.id, title=n.title, txt=n.text))
        return res

    @GEDCOM_line_breaks
    def _write_obj_lastchange(self, obj, level=1):
        res = []
        res.append('{l} CHAN'.format(l=level))
        res.append('{l1} DATE {dt}'.format(
            l1=level+1, dt=self.write_date(obj.date_changed)))

        return res
