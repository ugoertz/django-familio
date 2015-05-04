import json

from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string

from dajaxice.decorators import dajaxice_register
import watson

from .models import Person, Place, Event, Family, PersonPlace


roleDict = {
    'p': Person,
    'e': Event,
    'l': Place,
    'f': Family,
}


@dajaxice_register(method="GET")
def popover_data(request, link):
    # pylint: disable=no-member

    for linktext, model, template in [
            ('/gen/person-view/', Person, 'person_mouseover.html'),
            ('/gen/pedigree/', Person, 'person_mouseover.html'),
            ('/gen/descendants/', Person, 'person_mouseover.html'),
            ]:
        i = link.find(linktext)
        if i != -1:
            try:
                pk = int(link[i+len(linktext):-1])
                p = model.objects.get(pk=pk)
            except ObjectDoesNotExist:
                return "Unbekannt"
            return render_to_string(
                    'genealogio/%s' % template,
                    {'person': p, })


@dajaxice_register(method="GET")
def autocomplete(request, q, role):
    if role and role[0] in roleDict.keys():
        results = watson.filter(roleDict[role[0]].objects.all(), q)

        # does the search string contain the beginning of a handle?
        handleStart = q.find(role[0].upper()+'_')
        handlePart = '' if handleStart == -1 else q[handleStart:]
        template = ':%s:`' + (q + ' %s`' if handleStart == -1
                              else q[:handleStart] + '%s`')

        return json.dumps([{'text': template % (role, x.handle),
                            'displayText': str(x), }
                           for x in results
                           if x.handle.startswith(handlePart)])

    return json.dumps([])


@dajaxice_register(method="GET")
def pplaces_lines(request, person_id):

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

    return json.dumps({'type': 'LineString', 'coordinates': places, })
