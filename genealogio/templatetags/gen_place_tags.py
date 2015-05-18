# -*- coding: utf8 -*-

from __future__ import unicode_literals

from collections import OrderedDict
from geopy.distance import distance as geopy_distance

from django import template
from django.contrib.gis.measure import D

from maps.models import Place
from genealogio.models import Person, PersonPlace

register = template.Library()

@register.inclusion_tag('genealogio/borndiedhere.rst')
def related_people(place):
    # pylint: disable=no-member
    born_here = Person.objects.filter(personplace__place=place,
                                      personplace__typ=PersonPlace.BIRTH)
    died_here = Person.objects.filter(personplace__place=place,
                                      personplace__typ=PersonPlace.DEATH)

    born_close_by = OrderedDict()
    died_close_by = OrderedDict()

    for typ, results in [
            (PersonPlace.BIRTH, born_close_by),
            (PersonPlace.DEATH, died_close_by),
            ]:
        # pylint: disable=no-member
        pl_close_by = PersonPlace.objects.exclude(place=place).filter(
                typ=typ,
                place__location__distance_lte=(place.location, D(km=50))
                ).select_related('place', 'person')
        print pl_close_by.query
        print len(pl_close_by)

        person_count = 0
        l = [(geopy_distance((ppl.place.location.y, ppl.place.location.x),
                             (place.location.y, place.location.x)),
             ppl.place.id,                                # for sorting
             ppl.person.last_name, ppl.person.first_name, # for sorting
             ppl.place, ppl.person) for ppl in pl_close_by]
        l.sort()
        for distance, _, _, _, pl, person in l:
            if not pl.id in results:
                results[pl.id] = {
                        'place': pl, 'distance': distance, 'persons': [], }
            results[pl.id]['persons'].append(person)
            person_count += 1
            if person_count >= 10:
                break

    return {'born_here': born_here,
            'died_here': died_here,
            'born_close_by': born_close_by,
            'died_close_by': died_close_by, }

