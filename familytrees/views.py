from django.views.generic import (View, )
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import (
        CreateView, DetailView, UpdateView, View, )

from base.views import CurrentSiteMixin, PaginateListView

from genealogio.models import Family

from .forms import (
        FTCreateForm, FTForm,
)
from .models import FamilyTree
from .tasks import create_pdf


class PublicFTList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):
    """Display list of all publically available familytrees."""

    model = FamilyTree
    paginate_by = 12

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(public=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['public_fts'] = True
        context['page_title'] = 'Öffentlich verfügbare Stammbäume'
        return context


class UserFTList(LoginRequiredMixin, CurrentSiteMixin, PaginateListView):
    """Display list of all familytree project authored by request.user."""

    model = FamilyTree
    paginate_by = 12

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(authors=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Meine Stammbäume'
        return context


class FTDetail(LoginRequiredMixin, CurrentSiteMixin, UpdateView):
    model = FamilyTree
    form_class = FTForm
    template_name_suffix = '_detail'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(authors=self.request.user)
        return qs

    def form_valid(self, form):
        if self.request.user in self.get_object().authors.all():
            return super().form_valid(form)
        else:
            raise PermissionDenied


class FTCreateView(LoginRequiredMixin, CreateView):
    model = FamilyTree
    form_class = FTCreateForm
    template_name_suffix = '_detail'

    def form_valid(self, form):
        # add author
        ft = form.save(commit=False)
        ft.obj = Family.objects.get(handle=form.cleaned_data['reference'])
        ft.save()
        ft.authors.add(self.request.user)

        return super().form_valid(form)


class CreatePDFView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        # pylint: disable=unsubscriptable-object
        ft = FamilyTree.objects.get(pk=int(self.kwargs['id']))
        if self.request.user not in ft.authors.all():
            raise PermissionDenied

        result = create_pdf.delay(ft.pk)
        ft.render_status = result.id
        ft.save()

        return HttpResponseRedirect(
            reverse('ft-detail', kwargs={'pk': ft.pk, }))
