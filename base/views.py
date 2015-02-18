""" Views for the base application """

from django.shortcuts import render
# from django.views.generic import View
# import watson
from genealogio.models import Person
from notaro.models import Note


def home(request):
    """ Default view for the root """

    # pylint: disable=no-member
    return render(request, 'base/home.html',
                  {'personen': Person.objects.all().order_by('-date_added')[:5],
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

