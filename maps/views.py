# -*- coding: utf8 -*-

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from .models import Place, CustomMap


class PlaceDetail(LoginRequiredMixin, DetailView):
    """Display details for a person."""

    model = Place


class CustomMapDetail(LoginRequiredMixin, DetailView):
    """Display details for a person."""

    model = CustomMap


