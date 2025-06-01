from django.urls import re_path

from books.ajax import GetFamilies

from .views import (
    PublicFTList, UserFTList, FTCreateView, FTDetail, CreatePDFView,
)

urlpatterns = (
    re_path(r'^publicfts/$', PublicFTList.as_view(),
        name='public-ft-list'),
    re_path(r'^myfts/$', UserFTList.as_view(),
        name='my-ft-list'),
    re_path(r'^ft-create/$',
        FTCreateView.as_view(), name='ft-create'),
    re_path(r'^ft-view/(?P<pk>\d+)/$',
        FTDetail.as_view(), name='ft-detail'),
    re_path(r'^create-pdf/(?P<id>\d+)/$',
        CreatePDFView.as_view(), name='ft-create-pdf'),
    re_path(r'^getfam/$',
        GetFamilies.as_view(),
        name="get-families"),
)
