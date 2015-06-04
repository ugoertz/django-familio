# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import division

import json

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from braces.views import LoginRequiredMixin
from django.views.generic import (
        CreateView, DetailView, ListView, UpdateView, )
from django.views.generic.detail import SingleObjectMixin

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit

from base.views import CurrentSiteMixin

from .forms import (
        BookCreateForm, BookForm,
        CollectionCreateForm, CollectionForm,
        ItemCreateForm, ItemForm, )
from .models import Book, Collection, Item


class PublicBookList(LoginRequiredMixin, CurrentSiteMixin, ListView):
    """Display list of all publically available books."""

    model = Book
    paginate_by = 12

    def get_queryset(self, *args, **kwargs):
        qs = super(PublicBookList, self).get_queryset(*args, **kwargs)
        qs = qs.filter(public=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super(PublicBookList, self).get_context_data(**kwargs)
        context['page_title'] = 'Öffentlich verfügbare Buchprojekte'
        return context


class UserBookList(LoginRequiredMixin, CurrentSiteMixin, ListView):
    """Display list of all book project authored by request.user."""

    model = Book
    paginate_by = 12

    def get_queryset(self, *args, **kwargs):
        qs = super(UserBookList, self).get_queryset(*args, **kwargs)
        qs = qs.filter(authors=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super(UserBookList, self).get_context_data(**kwargs)
        context['page_title'] = 'Meine Buchprojekte'
        return context


class BookDetail(LoginRequiredMixin, CurrentSiteMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name_suffix = '_detail'

    def get_queryset(self):
        qs = super(BookDetail, self).get_queryset()
        qs = qs.filter(authors=self.request.user)
        return qs

    def form_valid(self, form):
        if self.request.user in self.get_object().authors.all():
            return super(BookDetail, self).form_valid(form)
        else:
            raise PermissionDenied


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookCreateForm
    template_name_suffix = '_detail'

    def form_valid(self, form):
        # add author
        book = form.save(commit=False)
        book.save()
        book.authors.add(self.request.user)

        if form.cleaned_data['populate'] != '-':
            book.populate(
                    form.cleaned_data['populate'],
                    form.cleaned_data['reference'])

        return super(BookCreateView, self).form_valid(form)


class CollectionDetail(LoginRequiredMixin, CurrentSiteMixin, UpdateView):
    model = Collection
    form_class = CollectionForm
    template_name_suffix = '_detail'

    def get_queryset(self):
        qs = super(CollectionDetail, self).get_queryset()
        qs = qs.filter(book__authors=self.request.user)
        return qs

    def form_valid(self, form):
        if self.request.user in self.get_object().book.authors.all():
            # analyze ordering and reorder/delete items, subcollections
            if form.cleaned_data['ordering']:
                ordering = json.loads(form.cleaned_data['ordering'])

                item_ids = [int(x[5:]) for x in ordering['items']]
                for item in self.get_object().item_set.all():
                    try:
                        item.position = item_ids.index(item.id)
                        item.save()
                    except ValueError:
                        item.delete()

                collection_ids = [int(x[5:]) for x in ordering['collections']]
                for collection in self.get_object().collection_set.all():
                    try:
                        collection.position = collection_ids.index(collection.id)
                        collection.save()
                    except ValueError:
                        collection.delete()

            return super(CollectionDetail, self).form_valid(form)
        else:
            raise PermissionDenied

    def get_initial(self):
        result = super(CollectionDetail, self).get_initial()
        result.update({'c_flags': self.get_object().get_flags_json(), })
        return result


class CollectionCreateView(LoginRequiredMixin, CreateView):
    model = Collection
    form_class = CollectionCreateForm
    template_name_suffix = '_detail'

    def form_valid(self, form):
        collection = form.save(commit=False)

        collection.parent = form.cleaned_data['parent']
        collection.save()

        if form.cleaned_data['model']:
            # populate collection as requested
            collection.populate()

        return super(CollectionCreateView, self).form_valid(form)

    def get_initial(self):
        result = super(CollectionCreateView, self).get_initial()
        parent = Collection.objects.get(id=int(self.kwargs['parent']))
        result.update({
            'parent': self.kwargs['parent'],
            'c_flags': parent.get_flags_json(),
            })
        return result


class ItemDetail(LoginRequiredMixin, CurrentSiteMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name_suffix = '_detail'

    def get_queryset(self):
        qs = super(ItemDetail, self).get_queryset()
        qs = qs.filter(parent__book__authors=self.request.user)
        return qs

    def form_valid(self, form):
        if self.request.user in self.get_object().parent.book.authors.all():
            return super(ItemDetail, self).form_valid(form)
        else:
            raise PermissionDenied

    def get_initial(self):
        result = super(ItemDetail, self).get_initial()
        result.update({'c_flags': self.get_object().get_flags_json(), })
        return result


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemCreateForm
    template_name_suffix = '_detail'

    def form_valid(self, form):
        item = form.save(commit=False)
        item.parent = form.cleaned_data['parent']
        item.save()

        return super(ItemCreateView, self).form_valid(form)

    def get_initial(self):
        result = super(ItemCreateView, self).get_initial()
        parent = Collection.objects.get(id=int(self.kwargs['parent']))
        result.update({
            'parent': self.kwargs['parent'],
            'c_flags': parent.get_flags_json(),
            })
        return result


class ItemRetrieveText(DetailView):

    model = Item

    def get(self, *args, **kwargs):
        obj = self.get_object()
        obj.set_text_from_template()
        return HttpResponseRedirect(obj.get_absolute_url())
