"""urlconf for the base application"""

from django.conf.urls import url, patterns

from .views import ToggleStaffView


urlpatterns = patterns('base.views',
                       url(r'^$', 'home', name='home'),
                       url(r'^toggle-staff-view/',
                           ToggleStaffView.as_view(),
                           name="toggle_staff_view"),
                       # url(r'^/s/$', SearchView.as_view(), name='search'),
                       )
