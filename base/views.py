# -*- coding: utf8 -*-

""" Views for the base application """

import os.path
import re

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ngettext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View

from django_transfer import TransferHttpResponse
from grappelli.views.related import (AutocompleteLookup, get_label,
                                     ajax_response, never_cache, )
from grappelli.settings import AUTOCOMPLETE_LIMIT

from accounts.models import UserSite
from genealogio.models import Person
from notaro.models import Note, Picture, Document
from comments.models import Comment


class PaginateListView(ListView):

    paginate_by = 12

    def get_paginate_by(self, queryset):
        try:
            return self.request.session['paginate_by']
        except:
            return self.paginate_by

    def get_paginator(self, *args, **kwargs):
        paginator = super(PaginateListView, self).get_paginator(
                *args, **kwargs)

        page = int(self.request.GET.get('page', 1))

        paginator.start_range = []
        paginator.start_main_dots = False
        paginator.main_range = range(1, paginator.num_pages+1)
        paginator.main_end_dots = False
        paginator.end_range = []

        start_main = 1
        end_main = paginator.num_pages

        if paginator.num_pages > 11:
            if page >= 7:
                paginator.start_range = range(1, 4)
                paginator.start_main_dots = True
                start_main = page - 2
                if page >= paginator.num_pages-2:
                    start_main = paginator.num_pages-4
            if page <= paginator.num_pages - 6:
                paginator.end_range = range(
                        paginator.num_pages-2, paginator.num_pages+1)
                paginator.main_end_dots = True
                end_main = page + 2
                if page <= 3:
                    end_main = 5
            paginator.main_range = range(start_main, end_main+1)
        return paginator


class CurrentSiteMixin(object):
    def get_queryset(self):
        qs = super(CurrentSiteMixin, self).get_queryset()
        try:
            return qs.filter(sites=self.request.site)
        except:
            return qs.filter(site=self.request.site)


def home(request):
    """ Default view for the root """

    if request.user.is_authenticated:
        try:
            calendar_range = settings.CALENDAR_RANGE
        except:
            calendar_range = 15

        # pylint: disable=no-member
        dates = [timezone.now().date() + (i-3) * timezone.timedelta(days=1)
                 for i in range(calendar_range)]
        birthdeathdays = [
                (d,
                 Person.objects
                 .filter(datebirth__endswith=d.strftime('-%m-%d')),
                 Person.objects
                 .filter(datedeath__endswith=d.strftime('-%m-%d')), )
                for d in dates]
        birthdeathdays = [(d, born, died)
                          for d, born, died in birthdeathdays if born or died]

        two_weeks_ago = timezone.now() - timezone.timedelta(days=14)
        assert timezone.is_aware(two_weeks_ago)
        context = {
                'personen':
                Person.objects.filter(date_changed__gt=two_weeks_ago)
                .order_by('-date_changed')[:5],
                'comments': Comment.objects.filter(
                    date__gt=two_weeks_ago).order_by('-date')[:5],
                'birthdeathdays': birthdeathdays,
                'today': timezone.now().date(),
                'notes':
                Note.objects.filter(
                    published=True, date_changed__gt=two_weeks_ago)
                .order_by('-date_changed')[:5],
                'pic_list': Picture.objects.all().order_by('?')[:9],
                }
    else:
        context = {}

    # pylint: disable=no-member
    return render(
            request, 'base/home.html',
            context)


protected_path = re.compile(r'\d+_')


def download(request, fname):
    # check permissions
    if not request.user.is_authenticated:
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
                               (Document, 'doc', 'documents'),
                               (Document, 'doc', 'images'),
                               (Document, 'image', 'documents'),
                               (Document, 'image', 'images'),
                               ]:
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


class CustomAutocompleteLookup(LoginRequiredMixin, AutocompleteLookup):
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

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        self.check_user_permission()
        self.GET = self.request.GET
        if self.request_is_valid():
            self.get_model()
            data = self.get_data(request)
            if data:
                return ajax_response(data)
        # overcomplicated label translation
        label = ngettext('%(counter)s result',
                          '%(counter)s results', 0) % {'counter': 0}
        data = [{"value": None, "label": label}]
        return ajax_response(data)


class ToggleStaffView(LoginRequiredMixin, View):
    """
    Toggle whether in templates the additional information, links, ... for
    staff members should be displayed. (If not, the page looks the same as for
    non-staff users.)

    The default is to display the staff information. This can be changed by the
    user in the "user dropdown menu" in navbar.
    """

    def post(self, request):
        if request.session.get('staff_view', True):
            request.session['staff_view'] = False
            # print('set false')
        else:
            request.session['staff_view'] = True
            # print('set true')
        return HttpResponseRedirect(request.POST.get('next', '/'))


class StorePaginateByView(LoginRequiredMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(StorePaginateByView, self).dispatch(*args, **kwargs)

    def post(self, request):
        if 'paginate_by' in request.POST:
            try:
                pb = int(request.POST['paginate_by'])
                assert pb > 0
                request.session['paginate_by'] = pb
            except:
                pass
        return HttpResponse()
