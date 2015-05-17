from django.views.generic import DetailView

from braces.views import LoginRequiredMixin

from .models import Place

class PlaceDetail(LoginRequiredMixin, DetailView):
    """Display details for a person."""

    model = Place


