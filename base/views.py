""" Views for the base application """

import datetime
from django.shortcuts import render
# from django.views.generic import View
# import watson
from genealogio.models import Person
from notaro.models import Note


def home(request):
    """ Default view for the root """

    # pylint: disable=no-member
    dates = [datetime.date.today() + (i-4) * datetime.timedelta(days=1)
             for i in range(20)]
    birthdeathdays = [
            (d,
             Person.objects
             .filter(datebirth__endswith=d.strftime('-%m-%d')),
             Person.objects
             .filter(datedeath__endswith=d.strftime('-%m-%d')), )
            for d in dates]
    birthdeathdays = [(d, born, died)
                      for d, born, died in birthdeathdays if born or died]

    # pylint: disable=no-member
    return render(
            request, 'base/home.html',
            {'personen': Person.objects.all().order_by('-date_added')[:5],
             'birthdeathdays': birthdeathdays, 
             'notes': Note.objects.filter(published=True)
                          .order_by('date_added')[:5], })


# class SearchView(View):

#     def get(self, request):
#         try:
#             q = request.GET.get('q')
#             results = watson.search(q)
#         except:
#             results = {}

#         return render(request, 'base/searchresults.html',
#                       {'searchterm': q, 'object_list': results, })

