"""urlconf for the base application"""

from django.urls import re_path

from .views import ToggleStaffView, StorePaginateByView, home
from .ajax import GetUserView

urlpatterns = (
        re_path(r'^$', home, name='home'),
        re_path(r'^toggle-staff-view/',
            ToggleStaffView.as_view(),
            name="toggle_staff_view"),
        re_path(r'^store-paginate-by/',
            StorePaginateByView.as_view(),
            name="store_paginate_by"),

        # ajax
        re_path(
            r'^getuser/$',
            GetUserView.as_view(),
            name="getuser"),
        )

