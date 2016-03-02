from __future__ import unicode_literals

import os
import os.path

from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.views.generic import (
        DetailView, TemplateView, UpdateView, View, )
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

from braces.views import LoginRequiredMixin
from filebrowser.base import FileListing

from base.views import CurrentSiteMixin, PaginateListView
from tags.models import CustomTag
from .models import Note, Picture, Source, Document, Video


class PictureDetail(LoginRequiredMixin, CurrentSiteMixin, UpdateView):
    """Display a picture."""

    model = Picture
    fields = ['caption', ]
    template_name_suffix = '_detail'

    def post(self, request, *args, **kwargs):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')
        return super(PictureDetail, self).post(request, *args, **kwargs)


class VideoDetail(LoginRequiredMixin, CurrentSiteMixin, UpdateView):
    """Display a video."""

    model = Video
    fields = ['caption', ]
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
    fields = ['name', 'description', ]
    template_name_suffix = '_detail'

    def post(self, request, *args, **kwargs):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')
        return super(DocumentDetail, self).post(request, *args, **kwargs)


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


class SourceList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):

    """Display list of all notes."""

    model = Source


class PictureList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):

    """Display list of all pictures."""

    model = Picture

    def get_context_data(self, **kwargs):
        context = super(PictureList, self).get_context_data(**kwargs)
        context.update({
            'size': self.kwargs.get('size', 'small'),
            'tag_list':
            CustomTag.objects
                     .all()
                     .annotate(num_times=Count('tags_customtagthrough_items'))
                     .order_by('-num_times', 'name')[:50],
            })

        return context


class VideoList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):

    """Display list of all pictures."""

    model = Video

    def get_context_data(self, **kwargs):
        context = super(VideoList, self).get_context_data(**kwargs)
        context.update({
            'tag_list':
            CustomTag.objects
                     .all()
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
        picture = Picture.objects.create(image=request.POST['filename'])
        picture.sites.add(request.site)

        return HttpResponseRedirect(picture.get_absolute_url())
