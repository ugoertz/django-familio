from __future__ import unicode_literals

import os
import os.path

from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView, View
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin
from filebrowser.base import FileListing

from base.views import CurrentSiteMixin
from tags.models import CustomTag
from .models import Note, Picture, Source, Document


class PictureDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display a picture."""

    model = Picture


class SourceDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display a source."""

    model = Source


class DocumentDetail(LoginRequiredMixin, CurrentSiteMixin, DetailView):
    """Display a source."""

    model = Document


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


class NoteList(LoginRequiredMixin, CurrentSiteMixin, ListView):

    """Display list of all notes."""

    model = Note
    paginate_by = 5

    def get_queryset(self):
        # pylint: disable=no-member
        return Note.objects.filter(published=True)


class DocumentList(LoginRequiredMixin, CurrentSiteMixin, ListView):

    """Display list of all notes."""

    model = Document
    paginate_by = 15


class SourceList(LoginRequiredMixin, CurrentSiteMixin, ListView):

    """Display list of all notes."""

    model = Source
    paginate_by = 15


class PictureList(LoginRequiredMixin, CurrentSiteMixin, ListView):

    """Display list of all notes."""

    model = Picture
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(PictureList, self).get_context_data(**kwargs)
        context.update({
            'size': self.kwargs.get('size', 'small'),
            'tag_list': CustomTag.objects.all(),
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
                 if x.filetype=='Image' and not x.url in pic_urls
                ]

        return render(
                request,
                "notaro/unbound_images_list.html",
                {'files': files, })

    def post(self, request):
        if not self.request.user.userprofile.is_staff_for_site:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        if not 'filename' in request.POST:
            messages.error(request, 'Es ist ein Fehler aufgetreten.')
            return HttpResponseRedirect('/')

        # create Picture object for filename
        # pylint: disable=no-member
        picture = Picture.objects.create(image=request.POST['filename'])
        picture.sites.add(request.site)

        return HttpResponseRedirect(picture.get_absolute_url())
