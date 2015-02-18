from __future__ import unicode_literals

# import os
# import os.path
# import csv
# import glob
# import datetime
import json

# from django import forms
# from django.http import HttpResponse, HttpResponseRedirect
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
                    'url': p.get_absolute_url(), }
            if level > 0:
                data['parents'] = [get_dict(p.get_father(), level-1),
                                   get_dict(p.get_mother(), level-1), ]

            return data

        data = get_dict(person, level=2)

        return render(request, 'genealogio/pedigree.html',
                      {'person': person, 'data': json.dumps(data), })
