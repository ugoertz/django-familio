from __future__ import unicode_literals

# from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView, View
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin

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
