# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division

import json

from dajaxice.decorators import dajaxice_register
import watson

from maps.models import Place
from genealogio.models import Person, Event, Family
from .models import CustomTag


# cannot have ',', '.' and '-' in tag texts
# this translator should be used by as_tag methods
def tag_translate(s):
    for c in '.,':
        s = s.replace(c, ' ')
    return s


@dajaxice_register(method="GET")
def get_tags(request, query):
    result_tags = CustomTag.objects.filter(
            name__startswith='tag-').values_list('name', flat=True)
    result_db = []
    if query:
        # pylint: disable=no-member
        result_db.extend(watson.filter(Person.objects.all(), query))
        result_db.extend(watson.filter(Family.objects.all(), query))
        result_db.extend(watson.filter(Event.objects.all(), query))
        result_db.extend(watson.filter(Place.objects.all(), query)[:15])
    all_tags = [{
        'id': '%s' % (tag, ),
        'label': tag[4:],
        'tag': tag[4:],
        'bg_color': '#eeeeee' } for tag in result_tags ]
    for x in result_db:
        tag, details = x.as_tag()
        all_tags.append({
            'id': tag_translate(tag) +\
                    ' %s.%s-%d' % (
                        x._meta.app_label, x._meta.model_name, x.pk),
            'label': details,
            'tag': tag_translate(tag),
            'bg_color': {
                'person': 'lightgreen',
                'family': 'lightblue',
                'event': 'yellow',
                'place': 'orange',
                }.get(x._meta.model_name, 'red'),
            })
    if not 'tag-%s' % query in result_tags and len(query) > 2:
        all_tags[0:0] = [{
            'id': 'new-%s' % query,
            'tag': '%s' % query,
            'label': '%s' % query,
            'bg_color': '#eeeeee', }]
    return json.dumps(all_tags)

