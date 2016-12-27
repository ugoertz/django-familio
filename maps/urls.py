from django.conf.urls import url

from .views import PlaceDetail, CustomMapDetail


urlpatterns = (
        url(r'^place-view/(?P<pk>\d+)/$',
            PlaceDetail.as_view(), name='place-detail'),
        url(r'^map-view/(?P<pk>\d+)/$',
            CustomMapDetail.as_view(), name='custommap-detail'),
        )

