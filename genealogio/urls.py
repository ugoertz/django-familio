from django.conf.urls import patterns, url

from .views import (
        PersonList, PersonDetail, EventDetail, FamilyList,
        Sparkline, Pedigree, HomeGeoJSON, FamilyDetail, PPlacesGeoJSON,
        Descendants)


urlpatterns = patterns('genealogio.views',
                       url(r'^persons/$', PersonList.as_view(),
                           name='person-list'),
                       url(r'^person-view/(?P<pk>\d+)/$',
                           PersonDetail.as_view(), name='person-detail'),
                       url(r'^families/$', FamilyList.as_view(),
                           name='family-list'),
                       url(r'^family-view/(?P<pk>\d+)/$',
                           FamilyDetail.as_view(), name='family-detail'),
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
                       url(r'^descendants/(?P<pk>\d+)/$',
                           Descendants.as_view(),
                           name='descendants'),
                       url(r'^sparkline-person/' +
                           r'(?P<pk>\d+)/(?P<fampk>\d+)/' +
                           r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
                           Sparkline.as_view(),
                           name='sparkline-person'),
                       url(r'^sparkline-head/' +
                           r'(?P<fampk>\d+)/' +
                           r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
                           Sparkline.as_view(),
                           name='sparkline-head'),
                       url(r'^sparkline-tlitem/' +
                           r'(?P<tlid>\d+)/' +
                           r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
                           Sparkline.as_view(),
                           name='sparkline-tlitem'), )

