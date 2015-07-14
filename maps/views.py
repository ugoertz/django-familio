# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from django.views.generic import DetailView

from braces.views import LoginRequiredMixin

from .models import Place, CustomMap


class PlaceDetail(LoginRequiredMixin, DetailView):
    """Display details for a person."""

    model = Place


class CustomMapDetail(LoginRequiredMixin, DetailView):
    """Display details for a person."""

    model = CustomMap


