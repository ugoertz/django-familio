# -*- coding: utf8 -*-

import datetime
import os
import os.path
import sys
from itertools import chain

from django.http import Http404, HttpResponseRedirect
from django.views.generic import (
        DetailView, TemplateView, UpdateView, View, )
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views.generic.list import ListView
from django.db.models import Count
from django.shortcuts import render

from filebrowser.base import FileListing, FileObject

from base.views import CurrentSiteMixin, PaginateListView
from tags.models import CustomTag
from partialdate.fields import PartialDate
from genealogio.models import Person, Event
from .models import Note, Picture, Source, Document, Video
from .forms import ThumbnailForm
from .tasks import create_document_thumbnail
# flake8: noqa


class PictureDetail(LoginRequiredMixin, CurrentSiteMixin, UpdateView):
    """Display a picture."""

    model = Picture
    fields = ['date', 'caption', ]
    template_name_suffix = '_detail'

    def post(self, request, *args, **kwargs):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')
        return super(PictureDetail, self).post(request, *args, **kwargs)


class VideoDetail(LoginRequiredMixin, CurrentSiteMixin, UpdateView):
    """Display a video."""

    model = Video
    fields = ['date', 'caption', ]
    template_name_suffix = '_detail'

    def post(self, request, *args, **kwargs):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')
        return super(VideoDetail, self).post(request, *args, **kwargs)


class SourceDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display a source."""

    model = Source


class DocumentDetail(LoginRequiredMixin, CurrentSiteMixin, UpdateView):
    """Display a source."""

    model = Document
    fields = ['name', 'date', 'description', ]
    template_name_suffix = '_detail'

    def get_context_data(self, **kwargs):
        context = super(DocumentDetail, self).get_context_data(**kwargs)
        context['thumbnail_form'] = ThumbnailForm(
                initial={'pk': self.get_object().pk, })
        return context

    def post(self, request, *args, **kwargs):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')
        return super(DocumentDetail, self).post(request, *args, **kwargs)


class CreateThumbnail(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        form = ThumbnailForm(request.POST)
        if form.is_valid():
            # pylint: disable=no-member
            doc = Document.objects.get(pk=form.cleaned_data['pk'])

            if not (doc.doc and doc.doc.filename[-4:].lower() == '.pdf'):
                messages.warning(
                        request,
                        'Vorschaubilder können nur für pdf-Dateien '
                        'erstellt werden.')
                return HttpResponseRedirect(
                        reverse(
                            'document-detail',
                            kwargs={'pk': form.cleaned_data['pk'], }))
            create_document_thumbnail.delay(
                    form.cleaned_data['pk'],
                    form.cleaned_data['page'])
            messages.success(
                    request,
                    'Das Vorschaubild wird nun erstellt. '
                    '(Bitte die Seite in ein, zwei Minuten neu laden.)')
            return HttpResponseRedirect(
                    reverse(
                        'document-detail',
                        kwargs={'pk': form.cleaned_data['pk'], }))
        else:
            messages.error(request, 'Bitte eine Seitenzahl angeben')
        try:
            return HttpResponseRedirect(
                    reverse(
                        'document-detail',
                        kwargs={'pk': request.POST['pk'], }))
        except:
            return HttpResponseRedirect(reverse('document-list'))


class NoteDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display a note."""

    model = Note


class NoteDetailVerboseLink(LoginRequiredMixin,
                            CurrentSiteMixin, TemplateView):
    """Display a note requested by the link in its link field."""

    template_name = 'notaro/note_detail.html'

    def get_context_data(self, **kwargs):
        context = super(NoteDetailVerboseLink, self).get_context_data(**kwargs)
        if not self.request.path_info.startswith('/n/'):
            raise Http404

        # pylint: disable=no-member
        link = self.request.path_info[2:]
        try:
            if self.request.user.is_staff:
                context['object'] = Note.objects.get(link=link)
            else:
                context['object'] = Note.objects.get(published=True, link=link)
        except ObjectDoesNotExist:
            raise Http404
        return context


class NoteList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):

    """Display list of all notes."""

    model = Note

    def get_queryset(self):
        # pylint: disable=no-member
        return Note.objects.filter(published=True)


class DocumentList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):

    """Display list of all notes."""

    model = Document

    def get_queryset(self):
        qs = super(DocumentList, self).get_queryset()

        # pylint: disable=all
        if 'order_by' in self.kwargs:
            if self.kwargs['order_by'] == 'date':
                qs = qs.order_by('date', 'id', )
            elif self.kwargs['order_by'] == 'datedesc':
                qs = qs.order_by('-date', '-id', )
            elif self.kwargs['order_by'] == 'added':
                qs = qs.order_by('-date_added', '-id', )
            elif self.kwargs['order_by'] == 'addeddesc':
                qs = qs.order_by('date_added', 'id', )
            elif self.kwargs['order_by'] == 'changed':
                qs = qs.order_by('-date_changed', '-id', )
            elif self.kwargs['order_by'] == 'changeddesc':
                qs = qs.order_by('date_changed', 'id', )
            elif self.kwargs['order_by'] == 'name':
                qs = qs.order_by('name', 'date', 'id', )
        return qs

    def get_context_data(self, **kwargs):
        context = super(DocumentList, self).get_context_data(**kwargs)

        context.update({
            'tag_list':
            CustomTag.objects
                     .filter(
                         tags_customtagthrough_items__content_type_id=
                         ContentType.objects.get_for_model(Document))
                     .annotate(num_times=Count('tags_customtagthrough_items'))
                     .order_by('-num_times', 'name')[:25],
            })

        return context


class SourceList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):

    """Display list of all notes."""

    model = Source


class PictureList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):

    """Display list of all pictures."""

    model = Picture

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'size': self.kwargs.get('size', 'small'),
            'tag_list':
            CustomTag.objects
                     .filter(
                         tags_customtagthrough_items__content_type_id=
                         ContentType.objects.get_for_model(Picture))
                     .annotate(num_times=Count('tags_customtagthrough_items'))
                     .order_by('-num_times', 'name')[:50],
            })

        return context


class PictureListUntagged(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):

    """Display list of all untagged pictures."""

    model = Picture
    template_name = 'notaro/picture_list.html'

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(tags=None)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'pagetitle': 'Bilder ohne Schlagwort',
            'size': self.kwargs.get('size', 'small'),
            'tag_list': [],
        })

        return context


class VideoList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):

    """Display list of all pictures."""

    model = Video

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'tag_list':
            CustomTag.objects
                     .filter(
                         tags_customtagthrough_items__content_type_id=
                         ContentType.objects.get_for_model(Video))
                     .annotate(num_times=Count('tags_customtagthrough_items'))
                     .order_by('-num_times', 'name')[:50],
            })

        return context


class UnboundImagesView(LoginRequiredMixin, View):
    """
    Display list of all files in _uploads/images which are not referenced by
    a Picture object.
    """

    def get(self, request):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        # pylint: disable=no-member
        pic_urls = [pic.image.url for pic in Picture.objects.all()]

        path = os.path.join(settings.FILEBROWSER_DIRECTORY, 'images')
        file_listing = FileListing(
                path, sorting_by='date', sorting_order='desc')
        files = [x for x in file_listing.files_walk_total()
                 if x.filetype == 'Image' and x.url not in pic_urls]

        return render(
                request,
                "notaro/unbound_images_list.html",
                {'files': files, })

    def post(self, request):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        if 'filename' not in request.POST:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        # create Picture object for filename
        # pylint: disable=no-member
        picture = Picture(image=FileObject(request.POST['filename']))
        picture.save()
        picture.sites.add(request.site)

        return HttpResponseRedirect(picture.get_absolute_url())

class SetDateFromEXIF(LoginRequiredMixin, View):

    def post(self, request, pk):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        try:
            pic = Picture.objects.get(pk=pk)
            d = pic.get_exif_data()[0].split(' ')[0]
            year = int(d[0:4])
            month = int(d[5:7])
            day = int(d[8:10])
            pic.date = PartialDate(year, month, day)
            pic.save()
            return HttpResponseRedirect(pic.get_absolute_url())
        except:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')

        try:
            return HttpResponseRedirect(pic.get_absolute_url())
        except:
            pass
        return HttpResponseRedirect('/')


class SearchForDateRange(LoginRequiredMixin, View):

    template_name = 'notaro/date_range.html'
    minimum_date = 1780
    maximum_date = datetime.datetime.today().year

    def get(self, request, fr=None, to=None, undated='N'):
        frval = fr or '1900'
        toval = to or '1950'

        toval = str(int(toval)+1)

        births = Person.objects.exclude(
                datebirth__lt=frval).exclude(datebirth__gte=toval)
        deaths = (Person.objects
                .exclude(datedeath__lt=frval)
                .exclude(datedeath__gte=toval)
                )
        events = Event.objects.exclude(date__lt=frval).exclude(date__gte=toval)
        pics = Picture.objects.exclude(date__lt=frval).exclude(date__gte=toval)
        videos = Video.objects.exclude(date__lt=frval).exclude(date__gte=toval)
        documents = Document.objects.exclude(
                date__lt=frval).exclude(date__gte=toval)
        if undated == 'Y':
            births = list(chain(
                births,
                Person.objects.filter(datebirth='')))
            deaths = list(chain(
                deaths,
                Person.objects.filter(datedeath='', probably_alive=False)))
            events = list(chain(events, Event.objects.filter(date='')))
            pics = list(chain(pics, Picture.objects.filter(date='')))
            videos = list(chain(videos, Video.objects.filter(date='')))
            documents = list(chain(
                documents, Document.objects.filter(date='')))

        return render(
                request,
                self.template_name,
                {
                    'slider_fr': max(int(fr), self.minimum_date),
                    'slider_to': min(int(to), self.maximum_date),
                    'fr': int(fr),
                    'to': int(to),
                    'minimum_date': self.minimum_date,
                    'maximum_date': self.maximum_date,
                    'undated': undated=='Y',
                    'births': births,
                    'deaths': deaths,
                    'events': events,
                    'pics': pics,
                    'videos': videos,
                    'documents': documents,
                    }
                )

    def post(self, request, fr=None, to=None, undated=None):
        try:
            fr, to  = request.POST['slider'].split(',')
            undated = 'Y' if ('showundated' in request.POST
                    and request.POST['showundated']) else 'N'
        except:
            return HttpResponseRedirect(reverse('date-range'))

        if int(fr) <= 1780:
            fr = '0001'
            if int(to) <= 1780:
                to = '1780'

        return HttpResponseRedirect(
                reverse(
                    'date-range',
                    kwargs={'fr': fr, 'to': to, 'undated': undated, }))

