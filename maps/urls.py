from django.conf.urls import patterns, url

from .views import PlaceDetail


urlpatterns = patterns('maps.views',
                       url(r'^place-view/(?P<pk>\d+)/$',
                           PlaceDetail.as_view(), name='place-detail'), )

