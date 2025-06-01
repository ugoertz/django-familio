import json

from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.generic import View

from watson import search as watson

from genealogio.models import Person, Family


class GetInstances(View):

    def get(self, request):
        query = self.request.GET['query']
        model = self.request.GET.get('model', None)

        try:
            model = ContentType.objects.get_for_id(model).model_class()
        except:
            return json.dumps([])

        # pylint: disable=no-member
        qs = watson.filter(model.objects.all(), query).distinct()
        return JsonResponse(
            [{'id': p.id, 'label': p.__str__(), } for p in qs],
            safe=False)


class GetPersonsFamilies(View):

    def get(self, request):

        query = self.request.GET['query']

        # pylint: disable=no-member
        qs_p = watson.filter(Person.objects.all(), query).distinct()
        qs_f = watson.filter(Family.objects.all(), query).distinct()

        result = JsonResponse(
            [{'id': x.handle,
              'label': '%s (%s-%s)' %
              (x.get_primary_name(), x.year_of_birth, x.year_of_death), }
             for x in qs_p] +
            [{'id': x.handle, 'label': 'Familie ' + x.__str__(), }
             for x in qs_f],
            safe=False
        )
        return result


class GetFamilies(View):

    def get(self, request):

        query = self.request.GET['query']

        # pylint: disable=no-member
        qs_f = watson.filter(Family.objects.all(), query).distinct()

        result = JsonResponse(
            [{
                'id': x.handle,
                'label': 'Familie %s' % str(x), }
             for x in qs_f],
            safe=False
        )
        return result
