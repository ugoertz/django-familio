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
# from django.core.exceptions import ObjectDoesNotExist
# from django.conf import settings
# from django.db.models import Sum
# from django.core.serializers.json import DateTimeAwareJSONEncoder
# from django.db.models.query import Q

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
        return 64

    timeline = [
        ["Wiener Kongress",                      [1815, [0, 0, 0]]],
        ["Deutsche Revolution 1848/49",          [1848, 1849, [1, 1, 0]]],
        ["Drittes Reich",                        [1933, 1945, [1, 0.5, 0]]],
        ["Deutsch-Französishcer Krieg",          [1870, 1871, [1, 0, 0, 0.8]]],
        ["Erfindung des Autos",                  [1886, [0, 0, 0]]],
        ["Erster Weltkrieg",                     [1914, 1918, [1, 0, 0, 0.8]]],
        ["Drittes Reich",                        [1933, 1945, [1, 0.5, 0]]],
        ["Zweiter Weltkrieg",                    [1939, 1945, [1, 0, 0, 0.8]]],
        ["Gründung von BRD und DDR",             [1949, [0, 0, 0]]],
        ["Gründung der EGKS (Montanunion)",      [1951, [0, 0, 0]]],
        ["Mauerbau",                             [1961, [0, 1, 0]]],
        ["Wiedervereinigung",                    [1990, [0, 0, 1]]],
        ["Einführung des Euro",                  [2002, [0, 0, 1]]]
    ]

    def get(self, request, pk, fr=None, to=None):

        # pylint: disable=no-member
        person = Person.objects.get(pk=pk)
        if not person.datebirth:
            return HttpResponse()

        BIRTH_YEAR = person.datebirth.year
        DEATH_YEAR = person.datedeath.year if person.datedeath\
            else datetime.date.today().year
        if fr is None:
            FROM_YEAR = person.datebirth.year - 10
        else:
            FROM_YEAR = int(fr)
        if to is None:
            TO_YEAR = (person.datedeath.year + 10) if person.datedeath\
                      else FROM_YEAR + 100
        else:
            TO_YEAR = int(to)

        def year_to_x(year):
            r = self.width/self.height *\
                (year - FROM_YEAR) / (TO_YEAR - FROM_YEAR)
            return r

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     self.width, self.height)

        ctx = cairo.Context(surface)
        ctx.scale(self.height/1.0, self.height/1.0)
        for key, value in Sparkline.timeline:
            ctx.move_to(year_to_x(value[0]), 0.5)
            ctx.line_to(year_to_x(value[1] if len(value) > 2
                        else value[0]+0.3), 0.5)
            ctx.set_source_rgba(*value[-1])
            ctx.set_line_width(0.3)
            ctx.stroke()

        ctx.set_line_width(0.02)
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(year_to_x(BIRTH_YEAR), 0.5)
        ctx.line_to(year_to_x(DEATH_YEAR), 0.5)
        ctx.close_path()
        ctx.stroke()

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
        for f in qs.exclude(start_date=''):
            ctx.rectangle(year_to_x(f.start_date.year)-0.1, 0.4, 0.2, 0.2)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
            ctx.set_source_rgb(0, 0, 0)
            ctx.rectangle(year_to_x(f.start_date.year)-0.1, 0.4, 0.2, 0.2)
            ctx.stroke()

        response = HttpResponse(content_type="image/png")
        surface.write_to_png(response)
        return response

