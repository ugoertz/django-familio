import json

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from dajaxice.decorators import dajaxice_register
import watson

from notaro.models import Document, Source
from genealogio.models import Person, Event, Family, TimelineItem


@dajaxice_register(method="GET")
def get_instances(request, query, model=None):

    try:
        model = ContentType.objects.get_for_id(model).model_class()
    except:
        return json.dumps([])

    # pylint: disable=no-member
    qs = watson.filter(model.objects.all(), query).distinct()
    return json.dumps([{'id': p.id, 'label': p.__unicode__(), } for p in qs])

@dajaxice_register(method="GET")
def get_persons_families(request, query):

    # pylint: disable=no-member
    qs_p = watson.filter(Person.objects.all(), query).distinct()
    qs_f = watson.filter(Family.objects.all(), query).distinct()

    result = json.dumps(
            [{'id': x.handle,
              'label': '%s (%s-%s)' %
              (x.get_primary_name(), x.year_of_birth, x.year_of_death), }
              for x in qs_p] +
            [{'id': x.handle, 'label': 'Familie ' + x.__unicode__(), }
                for x in qs_f])
    return result

