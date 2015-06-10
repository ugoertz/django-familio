""" Views for the base application """

import datetime
import os.path
import re
from django.shortcuts import render
from django.http import Http404
from django.conf import settings
from django.utils.translation import ungettext
from django.contrib.sites.models import Site
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
        try:
            return qs.filter(sites=self.request.site)
        except:
            return qs.filter(site=self.request.site)


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
                          .order_by('-date_added')[:5], })

protected_path = re.compile('\d+_')


def download(request, fname):
    # check permissions
    if not request.user.is_authenticated():
        raise Http404

    if fname.startswith('tmp') or fname.startswith('latex'):
        # The latex and tmp directories are used to store the pdfexport related
        # files. Those files that should be served to users will be copied to
        # another directory.
        raise Http404

    # for files within a filebrowser-versions directory, check permissions
    # based on the relative path
    if fname.startswith('%d_versions/' % settings.SITE_ID):
        fn = fname[len('%d_versions/' % settings.SITE_ID):]
    else:
        fn = fname

    if protected_path.match(fn) is None:
        # this subdirectory is available without restriction
        # (versions for uploads to current site, and non-protected directories)
        return TransferHttpResponse(os.path.join(settings.MEDIA_ROOT, fname))

    if (fn.startswith('%d_uploads/' % settings.SITE_ID) or
        fn.startswith('%d_pdfs/' % settings.SITE_ID)):
        # the upload/pdfs directory for the current site;
        # available without restrictions
        return TransferHttpResponse(os.path.join(settings.MEDIA_ROOT, fname))

    # in remaining cases, we have to find object corresponding to this file in
    # the database, and check its sites field

    # currently, this concerns filebrowser files attached to Picture or
    # Document objects
    for model, field, path in [(Picture, 'image', 'images'),
                               (Document, 'doc', 'documents')]:
        if fname[fname.find('_'):].startswith('_versions/'):
            # if the file sits in a versions directory, remove the version
            # suffix
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

    raise Http404


class CustomAutocompleteLookup(AutocompleteLookup):
    """ patch grappelli's autocomplete to let us control the queryset 
    by creating a autocomplete_queryset function on the model """

    def get_queryset(self, request=None):
        if self.model == Site and request and\
                not request.user.is_superuser:
            qs = request.user.userprofile.sites.filter(
                    usersite__role__in=[UserSite.STAFF,
                                        UserSite.SUPERUSER, ])
        elif request and not request.user.is_superuser:
            try:
                qs = self.model._default_manager.on_site()
            except:
                qs = self.model._default_manager.all()
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

