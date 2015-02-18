from __future__ import unicode_literals

# from django.shortcuts import render
from django.http import Http404
from django.views.generic import DetailView, ListView, TemplateView
from django.core.exceptions import ObjectDoesNotExist
from braces.views import LoginRequiredMixin

from .models import Note


class NoteDetail(LoginRequiredMixin, DetailView):
    """Display a note."""

    model = Note


class NoteDetailVerboseLink(LoginRequiredMixin, TemplateView):
    """Display a note requested by the link in its link field."""

    template_name = 'notaro/note_detail.html'

    def get_context_data(self, **kwargs):
        context = super(NoteDetailVerboseLink, self).get_context_data(**kwargs)
        if not self.request.path_info.startswith('/n/'):
            raise Http404
        link = self.request.path_info[2:]
        try:
            if self.request.user.is_staff:
                context['object'] = Note.objects.get(link=link)
            else:
                context['object'] = Note.objects.get(published=True, link=link)
        except ObjectDoesNotExist:
            raise Http404
        return context


class NoteList(LoginRequiredMixin, ListView):

    """Display list of all notes."""

    model = Note
    paginate_by = 5

    def get_queryset(self):
        return Note.objects.filter(published=True)

