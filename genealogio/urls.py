from django.conf.urls import patterns, url

from .views import PersonList, PersonDetail, PlaceDetail, EventDetail
from .views import FamilyList, Sparkline
from .views import Pedigree, HomeGeoJSON, FamilyDetail, PPlacesGeoJSON


urlpatterns = patterns('genealogio.views',
                       url(r'^persons/$', PersonList.as_view(),
                           name='person-list'),
                       url(r'^person-view/(?P<pk>\d+)/$',
                           PersonDetail.as_view(), name='person-detail'),
                       url(r'^families/$', FamilyList.as_view(),
                           name='family-list'),
                       url(r'^family-view/(?P<pk>\d+)/$',
                           FamilyDetail.as_view(), name='family-detail'),
                       url(r'^place-view/(?P<pk>\d+)/$',
                           PlaceDetail.as_view(), name='place-detail'),
                       url(r'^event-view/(?P<pk>\d+)/$',
                           EventDetail.as_view(), name='event-detail'),
                       url(r'^pp-data.geojson$',
                           PPlacesGeoJSON.as_view(),
                           name='personplaces-data'),
                       url(r'^data.geojson$',
                           HomeGeoJSON.as_view(),
                           name='data'),
                       url(r'^pedigree/(?P<pk>\d+)/$', Pedigree.as_view(),
                           name='pedigree'),
                       url(r'^sparkline/(?P<pk>\d+)/$', Sparkline.as_view(),
                           name='sparkline'),
                       url(r'^sparkline/' +
                           r'(?P<pk>\d+)/' +
                           r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
                           Sparkline.as_view(),
                           name='sparkline'), )

