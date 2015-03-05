""" Views for the base application """

import datetime
import os.path
from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils.translation import ungettext
from django.contrib.sites.models import Site
# from django.views.generic import View
# import watson
from django_transfer import TransferHttpResponse

from grappelli.views.related import (AutocompleteLookup, get_label,
                                     ajax_response, never_cache, )
from grappelli.settings import AUTOCOMPLETE_LIMIT

from accounts.models import UserSite
from genealogio.models import Person
from notaro.models import Note, Picture, Document
from comments.models import Comment


class CurrentSiteMixin(object):
    def get_queryset(self):
        qs = super(CurrentSiteMixin, self).get_queryset()
        return qs.filter(sites=self.request.site)


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
             'comments': Comment.objects.all().order_by('-date')[:5],
             'birthdeathdays': birthdeathdays,
             'today': datetime.date.today(),
             'notes': Note.objects.filter(published=True)
                          .order_by('date_added')[:5], })


def download(request, fname):
    # check permissions

    if fname.startswith(str(settings.SITE_ID)):
        # this is the easy case
        return TransferHttpResponse(os.path.join(settings.MEDIA_ROOT, fname))

    # if object does not belong to current site,
    # we have to check where this file belongs

    for model, field, path in [(Picture, 'image', 'images'),
                               (Document, 'doc', 'documents')]:
        if fname[fname.find('_'):].startswith('_versions/%s/' % path) or\
                fname[fname.find('_'):].startswith('_uploads/%s/' % path):

            fn = ('%d_uploads' % settings.SITE_ID) + fname[fname.find('/'):]
            if fname[fname.find('_'):].startswith('_versions/'):
                for v in ['_admin_thumbnail.', '_thumbnail.', '_small.',
                          '_medium.', '_big.', '_large.']:
                    fn = fn.replace(v, '.')

            # pylint: disable=no-member
            ps = model.objects.filter(**{field+'__startswith': fn, })
            for p in ps:
                if fname == getattr(p, field).path or\
                        fname in getattr(p, field).versions():
                    # found the right object
                    if request.site in p.sites.all():
                        return TransferHttpResponse(
                                os.path.join(settings.MEDIA_ROOT, fname))
                    else:
                        break

    return HttpResponseForbidden()


class CustomAutocompleteLookup(AutocompleteLookup):
    """ patch grappelli's autocomplete to let us control the queryset 
    by creating a autocomplete_queryset function on the model """

    def get_queryset(self, request=None):
        if self.model == Site and request and\
                not request.user.is_superuser:
            qs = request.user.userprofile.sites.filter(
                    usersite__role__in=[UserSite.STAFF,
                                        UserSite.SUPERUSER, ])
        else:
            qs = self.model._default_manager.all()
        qs = self.get_filtered_queryset(qs)
        qs = self.get_searched_queryset(qs)
        return qs.distinct()

    def get_data(self, request=None):
        return [{"value": f.pk, "label": get_label(f)}
                for f in self.get_queryset(request)[:AUTOCOMPLETE_LIMIT]]

    @never_cache
    def get(self, request, *args, **kwargs):
        self.check_user_permission()
        self.GET = self.request.GET
        if self.request_is_valid():
            self.get_model()
            data = self.get_data(request)
            if data:
                return ajax_response(data)
        # overcomplicated label translation
        label = ungettext('%(counter)s result',
                          '%(counter)s results', 0) % {'counter': 0}
        data = [{"value": None, "label": label}]
        return ajax_response(data)

# class SearchView(View):

#     def get(self, request):
#         try:
#             q = request.GET.get('q')
#             results = watson.search(q)
#         except:
#             results = {}

#         return render(request, 'base/searchresults.html',
#                       {'searchterm': q, 'object_list': results, })

