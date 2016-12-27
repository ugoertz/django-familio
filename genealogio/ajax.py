# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division

import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import View

from watson import search as watson

from maps.models import Place
from notaro.models import Document, Source
from .models import Person, Event, Family, PersonPlace

roleDict = {
    'p': Person,
    'e': Event,
    'l': Place,
    'f': Family,
    's': Source,
    'd': Document,
}


class PopoverData(View):

    def get(self, request):
        """
        Make link an optional argument since we want to use {% url %} in
        templates to retrieve first part of url and add "link" via javascript.
        """

        # pylint: disable=no-member

        link = request.GET['link']

        for linktext, model, template in [
                ('/gen/person-view/', Person, 'person_mouseover.html'),
                ('/gen/pedigree/', Person, 'person_mouseover.html'),
                ('/gen/descendants/', Person, 'person_mouseover.html'),
                ('/gen/family-view/', Family, 'family_mouseover.html'),
                ]:
            i = link.find(linktext)
            if i != -1:
                try:
                    pk = int(link[i+len(linktext):-1])
                    p = model.objects.get(pk=pk)
                except ObjectDoesNotExist:
                    return JsonResponse("Unbekannt", safe=False)
                return JsonResponse(render_to_string(
                        'genealogio/%s' % template,
                        {'object': p, 'request': request, }), safe=False)


class AutocompleteView(View):

    def get(self, request):

        q = self.request.GET['q']
        role = self.request.GET.get('role', '')
        if role and role[0] in roleDict.keys():
            results = watson.filter(roleDict[role[0]].objects.all(), q)

            # does the search string contain the beginning of a handle?
            handleStart = q.find(role[0].upper()+'_')
            handlePart = '' if handleStart == -1 else q[handleStart:]

            if role[0] in ['d', 's']:
                # Looking up Document or Source, so work with id instead of handle
                template = ':%s:`' + q + ' %s`'
                return json.dumps([{'text': template % (role, x.id),
                                    'displayText': str(x), }
                                for x in results])
            else:
                # For all other models, work with handle
                template = ':%s:`' + (q + ' %s`' if handleStart == -1
                                    else q[:handleStart] + '%s`')
                return JsonResponse([{'text': template % (role, x.handle),
                                    'displayText': str(x), }
                                for x in results
                                if x.handle.startswith(handlePart)], safe=False)

        return JsonResponse.dumps([], safe=False)


class PPlacesLines(View):

    def get(self, request, person_id):

        # pylint: disable=no-member
        person = Person.objects.get(id=person_id)
        ppl = person.personplace_set\
                    .exclude(typ__in=[PersonPlace.BIRTH,
                            PersonPlace.DEATH, ])\
                    .order_by('start')

        def coord(place):
            return [place.place.location.x, place.place.location.y, ]

        places = []
        try:
            places.append(coord(person.personplace_set.get(typ=PersonPlace.BIRTH)))
        except:
            pass
        for place in ppl:
            places.append(coord(place))
        try:
            places.append(coord(person.personplace_set.get(typ=PersonPlace.DEATH)))
        except:
            pass

        return JsonResponse({'type': 'LineString', 'coordinates': places, })
