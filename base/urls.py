"""urlconf for the base application"""

from django.conf.urls import url, patterns

from .views import ToggleStaffView, StorePaginateByView


urlpatterns = patterns('base.views',
                       url(r'^$', 'home', name='home'),
                       url(r'^toggle-staff-view/',
                           ToggleStaffView.as_view(),
                           name="toggle_staff_view"),
                       url(r'^store-paginate-by/',
                           StorePaginateByView.as_view(),
                           name="store_paginate_by"),
                       )
