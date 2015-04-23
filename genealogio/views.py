# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import division

import os
import os.path
# import glob
import datetime
import math
import cairocffi as cairo
import json

# from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.template import Template, Context
# from django.template.loader import get_template
# from django.core.mail import send_mail, send_mass_mail
# from django.db.models import Sum
# from django.core.serializers.json import DateTimeAwareJSONEncoder
# from django.db.models.query import Q

# from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.db.models import Count
from django.http import HttpResponse  # , HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, View
from django.shortcuts import render
from django.template.loader import render_to_string
from braces.views import LoginRequiredMixin
from djgeojson.views import GeoJSONLayerView

from base.views import CurrentSiteMixin

from notaro.models import Note, Source
from .models import Person, PersonPlace, Place, Event, Family, TimelineItem


class HomeGeoJSON(LoginRequiredMixin, GeoJSONLayerView):
    model = Place
    geometry_field = 'location'
    properties = ['title', 'typ', ]
    bbox_auto = True

    def get_queryset(self):

        # pylint: disable=no-member
        p_birth = set(PersonPlace.objects.filter(
            person__sites=Site.objects.get_current(), typ=PersonPlace.BIRTH)
            .values_list('place', flat=True))
        # pylint: disable=no-member
        p_death = set(PersonPlace.objects.filter(
            person__sites=Site.objects.get_current(), typ=PersonPlace.DEATH)
            .values_list('place', flat=True))

        p_combined = p_birth | p_death

        qs = Place.objects.filter(id__in=p_combined)\
            .filter(personplace__person__sites=Site.objects.get_current(),
                    personplace__typ__in=[PersonPlace.BIRTH,
                                          PersonPlace.DEATH])\
            .annotate(num=Count('personplace'))

        def get_t(n):
            if n >= 9:
                return '9'
            elif n >= 6:
                return '6'
            elif n >= 3:
                return '3'
            return ''

        for p in qs:
            if p.id in p_birth and p.id in p_death:
                p.typ = 'birthdeath' + get_t(p.num)
            elif p.id in p_death:
                p.typ = 'death' + get_t(p.num)
            else:
                p.typ = 'birth' + get_t(p.num)

        return qs


class PPlacesGeoJSON(LoginRequiredMixin, GeoJSONLayerView):
    model = Place
    geometry_field = 'location'
    properties = ['title', 'typ', ]
    bbox_auto = True

    def get_queryset(self):
        # pylint: disable=no-member
        person = Person.objects.get(id=self.request.GET['person_id'])

        qs = person.places.all().distinct()
        for p in qs:
            if p.personplace_set.filter(
                    person=person, typ=PersonPlace.BIRTH).exists():
                if p.personplace_set.filter(
                        person=person, typ=PersonPlace.DEATH).exists():
                    p.typ = 'birthdeath'
                else:
                    p.typ = 'birth'
            elif p.personplace_set.filter(
                    person=person, typ=PersonPlace.DEATH).exists():
                p.typ = 'death'
            else:
                # for other places choose the type according to order
                # specified in model definition (i.e., by start date)
                p.typ = p.personplace_set.filter(
                        person=person)[0].typ
        return qs


class PersonList(LoginRequiredMixin, CurrentSiteMixin, ListView):
    """Display list of all persons."""

    model = Person
    paginate_by = 12


class FamilyList(LoginRequiredMixin, CurrentSiteMixin, ListView):
    """Display list of all persons."""

    model = Family
    paginate_by = 12


class PersonDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display details for a person."""

    model = Person


class FamilyDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display details for a family."""

    model = Family

    @staticmethod
    def get_timeline_items(objid, fr, to):
        # pylint: disable=no-member
        timeline = TimelineItem.objects.filter(families__isnull=True) |\
                   TimelineItem.objects.filter(families=objid)
        timeline = timeline.order_by('start_date', 'end_date', 'title')

        # not so beautiful, but we cannot filter on properties:
        timeline = [ x for x in timeline if fr <= x.end and x.start <= to]
        return timeline

    @staticmethod
    def get_legref(timeline, fr=0, to=3000, latex=False, label=''):
        image_directive = 'sparklineimg' if latex else 'image'

        legref = ''

        # pylint: disable=no-member
        legref += '\n\n'.join(['.. |T%02d%s| replace::\n' % (x.id, label) +
                               '   :cabin:`%s` |br| :cabin:`%s`'
                               % (x.title, x.period)
                               for x in timeline])
        legref += '\n\n'
        legref += '\n\n'.join([
            '.. |Tmg%02d%s| %s:: %s'
            % (x.id, label, image_directive,
               reverse('sparkline-tlitem', kwargs={'tlid': x.id, 'fr': fr, 'to': to, }))
            for x in timeline])

        legref += '\n\n'
        legref += '\n\n'.join(['.. _T%02d%s: %s' % (x.id, label, x.url)
                               for x in timeline if x.url])
        legref += '\n\n'

        return legref


    @classmethod
    def get_context_data_for_object(cls, obj, latex=False):
        context = {}

        # NOTE: The 2110 is hard-coded in the template: below, 10 is subtracted
        # from fr, and the resulting value passed to the template. If in the
        # template, the value of fr is 2100, then no time line is displayed.
        fr = 2110
        to = 1200
        try:
            if obj.father and not obj.father.datedeath\
                    and obj.father.probably_alive:
                to = datetime.date.today().year + 2
            else:
                to = max(to, obj.father.datedeath.year)
        except:
            pass
        try:
            fr = min(fr, obj.father.datebirth.year)
            to = max(to, fr + 80)
        except:
            pass
        try:
            if obj.mother and not obj.mother.datedeath\
                    and obj.mother.probably_alive:
                to = datetime.date.today().year + 2
            else:
                to = max(to, obj.mother.datedeath.year)
        except:
            pass
        try:
            fr = min(fr, obj.mother.datebirth.year)
            to = max(to, fr + 80)
        except:
            pass

        for ch in obj.person_set.all():
            try:
                if not ch.datedeath and ch.probably_alive:
                    to = datetime.date.today().year + 2
                else:
                    to = max(to, ch.datedeath.year)
            except:
                pass

        fr = fr - 10
        context['fr'] = fr
        to = min(max(to + 5, fr + 80), datetime.date.today().year + 2)
        context['to'] = to

        timeline = cls.get_timeline_items(obj.id, fr, to)

        l = ['| |T%02d%04d|%s    | |Tmg%02d%04d|                    |\n'
                % (x.id, obj.id, '_' if x.url else ' ', x.id, obj.id)
                for x in timeline]
        l.append('\n')

        legend = '+---------------+--------------------------------+\n'.join(l)

        context['sparkline_legend'] = legend
        context['sparkline_legend_ref'] = cls.get_legref(
                timeline,
                fr=fr, to=to,
                latex=latex,
                label='%04d' % obj.id)

        return context

    def get_context_data(self, **kwargs):
        context = super(FamilyDetail, self).get_context_data(**kwargs)
        obj = self.get_object()
        context.update(self.get_context_data_for_object(obj))

        return context


class PlaceDetail(LoginRequiredMixin, DetailView):
    """Display details for a person."""

    model = Place


class EventDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display details for a person."""

    model = Event


class Pedigree(LoginRequiredMixin, View):
    """Display pedigree for a person."""

    def get(self, request, pk):
        # pylint: disable=no-member
        person = Person.objects.get(pk=pk)

        def get_dict(p, level=0):
            if level < 0:
                return
            if p is None:
                return {'name': '', 'born': '', 'died': '', 'url': '', }
            data = {'name': p.get_primary_name(),
                    'born': p.datebirth.year if p.datebirth else '',
                    'died': p.datedeath.year if p.datedeath else '',
                    'url': p.get_absolute_url(),
                    'urlp': reverse("pedigree", kwargs={"pk": p.id, }),
                    }
            if level > 0:
                data['parents'] = [get_dict(p.get_father(), level-1),
                                   get_dict(p.get_mother(), level-1), ]

            return data

        data = get_dict(person, level=2)

        return render(request, 'genealogio/pedigree.html',
                      {'person': person, 'data': json.dumps(data), })


class Descendants(LoginRequiredMixin, View):
    """Display descendants of a person."""

    def get(self, request, pk):
        # pylint: disable=no-member
        person = Person.objects.get(pk=pk)
        height = 0

        def p_dict(person, suffix):
            try:
                return {
                    'name' + suffix: person.get_primary_name(),
                    'born' + suffix:
                    person.datebirth.year if person.datebirth else '',
                    'died' + suffix:
                    person.datedeath.year if person.datedeath else '',
                    'url' + suffix: person.get_absolute_url(),
                    'urlp' + suffix:
                    reverse("descendants", kwargs={"pk": person.id, }),
                    }
            except:
                pass
            return {
                'name' + suffix: person or '',
                'born' + suffix: '',
                'died' + suffix: '',
                'url' + suffix: '',
                'urlp' + suffix: None
                }

        def get_dict(p, level=0):
            """Returns a list of dictionaries, one for each family where p is
            father or mother."""

            if level < 0:
                return 1, None
            if p is None:
                return 0, {}

            data = [p_dict(p, '1')]
            fams = p.get_children()
            height = 0

            def add_family(data, family):
                height = 0
                partner, children, _text, _family = family
                data[-1].update(p_dict(partner, '2'))
                if not children:
                    data[-1]['urlp1'] = None
                    data[-1]['urlp2'] = None

                if level > 0:
                    data[-1]['parents'] = []
                    for ch in children:
                        h, d = get_dict(ch, level-1)
                        height += h
                        data[-1]['parents'].extend(d)
                    else:
                        height += 1
                return height

            if fams:
                height += add_family(data, fams[0])
            else:
                # no children, so delete link to descendants view for
                # this person
                data[-1]['urlp1'] = None
            for family in fams[1:]:
                # Now handle other families
                # Here, replace name of p by '...'
                data.append(p_dict('...', '1'))
                height += add_family(data, family)

            return height+2, data

        if person.get_children():
            height, d = get_dict(person, level=2)
            data = {'parents': d, }
        else:
            height = 0
            data = []
        # print json.dumps(data, indent=4)

        return render(request, 'genealogio/descendants.html',
                      {'person': person,
                       'height': height * 30,
                       'data': json.dumps(data), })


class Sparkline(LoginRequiredMixin, View):

    """Sparkline view. """

    width =  512
    height = 32

    def get(self, request, fampk=None, pk=None, tlid=None, fr=None, to=None):
        response = HttpResponse(content_type="image/png")
        surface = self.get_image(fampk=fampk, pk=pk, tlid=tlid, fr=fr, to=to)
        surface.write_to_png(response)
        return response

    @classmethod
    def get_image(cls, fampk=None, pk=None, tlid=None,
                  fr=None, to=None, width=None, height=None):
        """
        If pk (== person's id) and fampk (== family's id) are both not None, then
        return sparkling image for that person/family.

        If pk is None but fampk is not None, then return the headline image for
        that family.

        If tlid is not None, then return image for the corresponding timeline item.
        """

        width = width or cls.width
        height = height or cls.height

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     width, height)

        if pk is not None and fampk is not None:
            # pk is the id of a Person object

            # pylint: disable=no-member
            try:
                person = Person.objects.get(pk=pk)
                if not person.datebirth:
                    # no date of birth known, so just display empty sparkline
                    return surface

                BIRTH_YEAR = person.datebirth.year
                if person.datedeath:
                    DEATH_YEAR = person.datedeath.year
                else:
                    DEATH_YEAR = min(BIRTH_YEAR+120,
                                     datetime.date.today().year)
                # if we do not have a deathdate, check whether it is plausible
                # that this person is still alive
                guess_dead = (
                        not person.datedeath
                        and (not person.probably_alive
                             or BIRTH_YEAR + 120 < datetime.date.today().year))
            except ObjectDoesNotExist:
                person = None
        else:
            person = None

        if fr is not None:
            FROM_YEAR = int(fr)
        elif person:
            FROM_YEAR = person.datebirth.year - 10
        else:
            FROM_YEAR = 1900

        if to is not None:
            TO_YEAR = int(to)
        elif person:
            TO_YEAR = (person.datedeath.year + 10) if person.datedeath\
                    else FROM_YEAR + 100
        else:
            TO_YEAR = 2020

        def year_to_x(year):
            r = width/height *\
                (year - FROM_YEAR) / (TO_YEAR - FROM_YEAR)
            return r

        ctx = cairo.Context(surface)
        ctx.scale(height/1.0, height/1.0)

        def draw_line(f, t, width, rgba=(0, 0, 0)):
            ctx.move_to(f, 0.5)
            ctx.line_to(t, 0.5)
            ctx.set_source_rgba(*rgba)
            ctx.set_line_width(width)
            ctx.stroke()

        if fampk is not None:
            # head or person
            for x in FamilyDetail.get_timeline_items(fampk, FROM_YEAR, TO_YEAR):
                draw_line(year_to_x(x.start-0.2),
                          year_to_x(x.end if x.end > x.start else x.start+0.2),
                          0.3,
                          x.color[:3] + [0.2 if pk is not None else 1, ])

        if pk is None:
            if tlid is None:
                # header line
                for i in range((FROM_YEAR-1)//10 + 1, TO_YEAR//10 + 1):
                    draw_line(year_to_x(i*10),
                              year_to_x(i*10)+0.02,
                              0.2)
                for i in range((FROM_YEAR-1)//100 + 1, TO_YEAR//100 + 1):
                    draw_line(year_to_x(i*100),
                              year_to_x(i*100)+0.06,
                              0.6)
            else:
                # single timeline item

                # pylint: disable=all
                x = TimelineItem.objects.get(id=int(tlid))

                draw_line(year_to_x(x.start-0.2),
                          year_to_x(x.end if x.end > x.start else x.start+0.2),
                          0.3,
                          x.color)

        elif person:
            if not guess_dead:
                # death date is known, or person is alive
                # draw solid life line
                draw_line(year_to_x(BIRTH_YEAR),
                          year_to_x(DEATH_YEAR),
                          0.04)
            else:
                # person is probably dead, but we do not have date of death
                # draw last part of corresponding line dashed
                # LIMIT determines where to switch from solid to dashed
                LIMIT = max(DEATH_YEAR - 20, (BIRTH_YEAR + DEATH_YEAR)/2)

                draw_line(year_to_x(BIRTH_YEAR),
                          year_to_x(LIMIT),
                          0.04)
                ctx.set_dash([0.08, 0.14], 0.04)
                draw_line(year_to_x(LIMIT),
                          year_to_x(DEATH_YEAR),
                          0.04)
                ctx.set_dash([])

            # draw limiter at birth year
            draw_line(year_to_x(BIRTH_YEAR),
                      year_to_x(BIRTH_YEAR)+0.04,
                      0.4)
            if person.datedeath:
                # draw limiter at death year
                draw_line(year_to_x(DEATH_YEAR),
                          year_to_x(DEATH_YEAR)+0.04,
                          0.4)

            for p, c, _t, _f in person.get_children():
                for child in c:
                    if not child.datebirth:
                        continue
                    ctx.set_source_rgb(0, 0, 0)
                    ctx.arc(year_to_x(child.datebirth.year),
                            0.5, 0.1, 0, 2*math.pi)
                    ctx.fill()

            # pylint: disable=no-member
            qs = Family.objects.filter(father=person) |\
                Family.objects.filter(mother=person)
            for f in qs.exclude(start_date='')\
                       .exclude(start_date__isnull=True):
                ctx.rectangle(year_to_x(f.start_date.year)-0.1, 0.4, 0.2, 0.2)
                ctx.set_source_rgb(1, 1, 1)
                ctx.fill()
                ctx.set_line_width(0.04)
                ctx.set_source_rgb(0, 0, 0)
                ctx.rectangle(year_to_x(f.start_date.year)-0.1, 0.4, 0.2, 0.2)
                ctx.stroke()

        return surface


def booktemplate():
    '''Returns a list of items of the following form:

    - headers: starts with 1_, 2_, 3_, ..., followed by the text of the header.
    - notes: note_%d % note.id
    - persons, families, events: handle
    - source: source_%d % source.id
    - timeline items: tlitem_%d % tlitem.id
    '''

    # pylint: disable=no-member
    texts = ['note_%d' % n.id for n in Note.objects.all()]
    persons = [p.handle for p in Person.objects.all()]
    families = [f.handle for f in Family.objects.all()]
    events = [e.handle for e in Event.objects.all()]
    sources = ['source_%d' % s.id for s in Source.objects.all()]
    tlitems = ['tlitem_%d' % tlitem.id for tlitem in TimelineItem.objects.all()]

    return (['1_Texte', ] + texts +
            ['1_Personen', ] + persons +
            ['1_Familien', ] + families +
            ['1_Ereignisse', ] + events +
            ((['1_Quellen', ] + sources) if sources else []) +
            ['1_Anhang', '2_Ereignisse in den Zeitstrahlen', ] + tlitems
            )


INDEX_TEMPLATE_HEADER = '''
=========================
Unsere Familiengeschichte
=========================

.. toctree::
    :maxdepth: 1

'''


INDEX_TEMPLATE_FOOTER = '\n'


def create_rst(btemplate=None):
    if btemplate is None:
        btemplate = booktemplate()
    if len(btemplate) == 0:
        return

    # TODO
    # use fabric here? -- ultimately want to run this in a different virtualenv
    # ...

    # TODO get some tmpdir where we put our sphinx project
    directory = 'pdfexport'
    chapters = []
    index = open(os.path.join(directory, 'index.rst'), 'w')
    index.write(INDEX_TEMPLATE_HEADER)

    has_families = False

    def close_chapter():
        if has_families:
            chapters[-1].write('\n\n.. |br| raw:: html\n\n  <br />\n\n')
        chapters[-1].close()

    def start_new_chapter():
        if chapters:
            close_chapter()
        index.write('    chapter_%d\n' % len(chapters))
        has_families = False
        chapters.append(open(os.path.join(directory,
                                          'chapter_%d.rst' % len(chapters)),
                             'w'))

    if not btemplate[0][:2] == '1_':
        # add first chapter here if the template does not start with a level-1
        # header
        start_new_chapter()

    for item in btemplate:
        # pylint: disable=no-member
        if item.startswith('note_'):
            obj = Note.objects.get(id=int(item[5:]))
            chapters[-1].write(render_to_string('notaro/note_detail.rst',
                                                {'object': obj,
                                                 'latexmode': True, }
                                                ).encode('utf8'))
            chapters[-1].write('\n\n')
        elif item.startswith('source_'):
            obj = Source.objects.get(id=int(item[7:]))
            chapters[-1].write(render_to_string('notaro/source_detail.rst',
                                                {'object': obj,
                                                 'latexmode': True, }
                                                ).encode('utf8'))
            chapters[-1].write('\n\n')
        elif item.startswith('tlitem_'):
            obj = TimelineItem.objects.get(id=int(item[7:]))
            chapters[-1].write(render_to_string('genealogio/tlitem_detail.rst',
                                                {'object': obj,
                                                 'latexmode': True, }
                                                ).encode('utf8'))
            chapters[-1].write('\n\n')
        elif item.startswith('P_'):
            obj = Person.objects.get(handle=item)
            chapters[-1].write(render_to_string(
                'genealogio/person_detail.rst', {'object': obj,
                                                 'latexmode': True, }
                                                ).encode('utf8'))
            chapters[-1].write('\n\n')
        elif item.startswith('F_'):
            obj = Family.objects.get(handle=item)
            context = {'object': obj, 'latexmode': True, }
            context.update(
                    FamilyDetail.get_context_data_for_object(obj, latex=True))
            has_families = True
            chapters[-1].write(render_to_string('genealogio/family_detail.rst',
                                                context).encode('utf8'))
            chapters[-1].write('\n\n')
        elif item.startswith('E_'):
            obj = Event.objects.get(handle=item)
            chapters[-1].write(render_to_string('genealogio/event_detail.rst',
                                                {'object': obj,
                                                 'latexmode': True, }
                                                ).encode('utf8'))
            chapters[-1].write('\n\n')
        elif item[:2] == '1_':
            start_new_chapter()
            chapters[-1].write('\n\n')
            chapters[-1].write('=' * len(item[2:]))
            chapters[-1].write('\n%s\n' % item[2:])
            chapters[-1].write('=' * len(item[2:]))
            chapters[-1].write('\n\n')
        elif item[:2] in ['1_', '2_', '3_', '4_', '5_']:
            c = '=-~`.:'[int(item[0])]
            chapters[-1].write('\n\n%s\n' % item[2:])
            chapters[-1].write(c * len(item[2:]))
            chapters[-1].write('\n\n')
        else:
            # unknown item - raise an exception?
            pass

    close_chapter()
    index.write(INDEX_TEMPLATE_FOOTER)
    index.close()
    return directory


def create_pdf(directory):
    '''In directory, run sphinx to create latex files, and then run xelatex.'''
    pass
