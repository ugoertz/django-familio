from django.urls import re_path

from .views import PlaceDetail, CustomMapDetail


urlpatterns = (
        re_path(r'^place-view/(?P<pk>\d+)/$',
            PlaceDetail.as_view(), name='place-detail'),
        re_path(r'^map-view/(?P<pk>\d+)/$',
            CustomMapDetail.as_view(), name='custommap-detail'),
        )

