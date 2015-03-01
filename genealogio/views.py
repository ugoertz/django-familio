# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import division

# import os
# import os.path
# import csv
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
# from django.conf import settings
# from django.db.models import Sum
# from django.core.serializers.json import DateTimeAwareJSONEncoder
# from django.db.models.query import Q

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse  # , HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, View
from django.shortcuts import render
from braces.views import LoginRequiredMixin
from djgeojson.views import GeoJSONLayerView

from .models import Person, PersonPlace, Place, Event, Family


class HomeGeoJSON(LoginRequiredMixin, GeoJSONLayerView):
    model = Place
    geometry_field = 'location'
    properties = ['title', 'typ', ]
    bbox_auto = True

    def get_queryset(self):

        # pylint: disable=no-member
        p_birth = set(PersonPlace.objects.filter(typ=PersonPlace.BIRTH)
                                         .values_list('place', flat=True))
        qs_birth = Place.objects.filter(id__in=p_birth)

        # pylint: disable=no-member
        p_death = set(PersonPlace.objects.filter(typ=PersonPlace.DEATH)
                                 .values_list('place', flat=True))
        qs_death = Place.objects.filter(id__in=p_death)

        qs = qs_birth | qs_death

        for p in qs:
            if p.id in p_birth:
                p.typ = 'birth'
            if p.id in p_death:
                p.typ = 'death'

        return qs


class PPlacesGeoJSON(LoginRequiredMixin, GeoJSONLayerView):
    model = Place
    geometry_field = 'location'
    properties = ['title', 'typ', ]
    bbox_auto = True

    def get_queryset(self):
        # pylint: disable=no-member
        person = Person.objects.get(id=self.request.GET['person_id'])

        return person.places.all().distinct()


class PersonList(LoginRequiredMixin, ListView):
    """Display list of all persons."""

    model = Person
    paginate_by = 12


class FamilyList(LoginRequiredMixin, ListView):
    """Display list of all persons."""

    model = Family
    paginate_by = 12


class PersonDetail(LoginRequiredMixin, DetailView):
    """Display details for a person."""

    model = Person


class FamilyDetail(LoginRequiredMixin, DetailView):
    """Display details for a person."""

    model = Family

    def get_context_data(self, **kwargs):
        context = super(FamilyDetail, self).get_context_data(**kwargs)
        obj = self.get_object()
        fr = 2100
        to = 1200
        try:
            fr = min(fr, obj.father.datebirth.year)
            to = max(to, obj.father.datedeath.year)
        except:
            pass
        try:
            fr = min(fr, obj.mother.datebirth.year)
            to = max(to, obj.mother.datedeath.year)
        except:
            pass

        for ch in obj.person_set.all():
            try:
                to = max(to, ch.datedeath.year)
            except:
                pass

        fr = fr - 10
        context['fr'] = fr
        to = min(max(to + 5, fr+80), datetime.date.today().year + 2)
        context['to'] = to

        def start(x):
            return x[1][0]

        def end(x):
            return x[1][0] if len(x[1]) == 2 else x[1][1]

        timeline = [x for x in Sparkline.timeline
                    if fr <= end(x) and start(x) <= to]
        l = ['||T%02d|_  | |Tmg%02d|                        |\n' % (i, i)
             for i in range(len(timeline))]
        l.append('\n')

        legend = '+--------+--------------------------------+\n'.join(l)
        legend += '\n'

        legend += '\n\n'.join(['.. |T%02d| replace::\n' % i +
                               '   :cabin:`%s` |br| :cabin:`%s`'
                               % (x[0], str(x[1][0]) if len(x[1]) == 2
                                  else '%s-%s' % tuple(x[1][:2]), )
                               for i, x in enumerate(timeline)])
        legend += '\n\n'
        legend += '\n\n'.join(['.. |Tmg%02d| image:: /gen/sparkline/%d/%d/%d/'
                               % (i, 100001 + i, fr, to)
                               for i in range(len(timeline))])

        legend += '\n\n'
        legend += '\n\n'.join(['.. _T%02d: %s' % (i, x[2])
                               for i, x in enumerate(timeline)])

        context['sparkline_legend'] = legend

        return context


class PlaceDetail(LoginRequiredMixin, DetailView):
    """Display details for a person."""

    model = Place


class EventDetail(LoginRequiredMixin, DetailView):
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


class Sparkline(LoginRequiredMixin, View):

    """Sparkline view. """

    @property
    def width(self):
        return 512

    @property
    def height(self):
        return 32

    timeline = [
        ["Wiener Kongress",                      [1815, [0, 0, 0]],
         'https://de.wikipedia.org/wiki/Wiener_Kongress'],
        ["Deutsche Revolution 1848/49",          [1848, 1849, [1, 0, 1]],
         'https://de.wikipedia.org/wiki/Deutsche_Revolution_1848/1849'],
        ["Deutsch-Französischer Krieg",          [1870, 1871, [1, 0, 0]],
         'https://de.wikipedia.org/wiki/Deutsch-Franz%C3%B6sischer_Krieg'],
        ["Erfindung des Autos",                  [1886, [0, 0, 0]],
         'https://de.wikipedia.org/wiki/Geschichte_des_Automobils'],
        ["Erster Weltkrieg",                     [1914, 1918, [1, 0, 0]],
         'https://de.wikipedia.org/wiki/Erster_Weltkrieg'],
        ["Drittes Reich",                        [1933, 1945, [1, 0.5, 0]],
         'https://de.wikipedia.org/wiki/Drittes_Reich'],
        ["Zweiter Weltkrieg",                    [1939, 1945, [1, 0, 0]],
         'https://de.wikipedia.org/wiki/Zweiter_Weltkrieg'],
        ["Gründung von BRD und DDR",             [1949, [0, 0, 0]],
         'https://de.wikipedia.org/wiki/' +
         'Nachkriegszeit_nach_dem_Zweiten_Weltkrieg_in_Deutschland'],
        ["Gründung der EGKS (Montanunion)",      [1951, [0, 0, 0]],
         'https://de.wikipedia.org/wiki/' +
         'Europ%C3%A4ische_Gemeinschaft_f%C3%BCr_Kohle_und_Stahl'],
        ["Mauerbau",                             [1961, [0, 1, 0]],
         'https://de.wikipedia.org/wiki/Berliner_Mauer'],
        ["Wiedervereinigung",                    [1990, [0, 0, 1]],
         'https://de.wikipedia.org/wiki/Deutsche_Wiedervereinigung'],
        ["Einführung des Euro",                  [2002, [0, 0, 1]],
         'https://de.wikipedia.org/wiki/Euro']
    ]

    def get(self, request, pk, fr=None, to=None):

        if int(pk) < 100000:
            # pylint: disable=no-member
            try:
                person = Person.objects.get(pk=pk)
                if not person.datebirth:
                    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                                 self.width, self.height)
                    response = HttpResponse(content_type="image/png")
                    surface.write_to_png(response)
                    return response

                BIRTH_YEAR = person.datebirth.year
                DEATH_YEAR = person.datedeath.year if person.datedeath\
                    else datetime.date.today().year
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
            r = self.width/self.height *\
                (year - FROM_YEAR) / (TO_YEAR - FROM_YEAR)
            return r

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     self.width, self.height)

        ctx = cairo.Context(surface)
        ctx.scale(self.height/1.0, self.height/1.0)

        def draw_line(f, t, width, rgba=(0, 0, 0)):
            ctx.move_to(f, 0.5)
            ctx.line_to(t, 0.5)
            ctx.set_source_rgba(*rgba)
            ctx.set_line_width(width)
            ctx.stroke()

        if int(pk) <= 100000:
            for key, value, _dummy in Sparkline.timeline:
                draw_line(year_to_x(value[0]),
                          year_to_x(value[1] if len(value) > 2
                          else value[0]+0.3),
                          0.3,
                          value[-1][:3] + [0.2 if int(pk) < 100000 else 1, ])

        if int(pk) >= 100000:
            if int(pk) == 100000:
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
                def start(x):
                    return x[1][0]

                def end(x):
                    return x[1][0] if len(x[1]) == 2 else x[1][1]

                timeline = [x for x in Sparkline.timeline
                            if FROM_YEAR <= end(x) and start(x) <= TO_YEAR]
                value = timeline[int(pk)-100001][1]
                draw_line(year_to_x(value[0]),
                          year_to_x(value[1] if len(value) > 2
                                    else value[0]+0.3),
                          0.3,
                          value[-1])

        elif person:
            draw_line(year_to_x(BIRTH_YEAR),
                      year_to_x(DEATH_YEAR),
                      0.04)
            draw_line(year_to_x(BIRTH_YEAR),
                      year_to_x(BIRTH_YEAR)+0.04,
                      0.4)
            if person.datedeath:
                draw_line(year_to_x(DEATH_YEAR),
                          year_to_x(DEATH_YEAR)+0.04,
                          0.4)

            for p, c, t in person.get_children():
                for child in c:
                    if not child.datebirth:
                        continue
                    ctx.set_source_rgb(0, 0, 0)
                    ctx.arc(year_to_x(child.datebirth.year),
                            0.5, 0.1, 0, 2*math.pi)
                    ctx.fill()

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

        response = HttpResponse(content_type="image/png")
        surface.write_to_png(response)
        return response

