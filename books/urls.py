from django.urls import re_path

from .views import (
        PublicBookList, UserBookList,
        BookCreateView, BookDetail, CreatePDFView,
        CollectionDetail, CollectionCreateView,
        ItemDetail, ItemCreateView, ItemRetrieveText,
        ExportGEDCOMView,
        )
from .ajax import (
        GetInstances, GetPersonsFamilies,
        )

urlpatterns = (
        re_path(r'^publicbooks/$', PublicBookList.as_view(),
            name='public-book-list'),
        re_path(r'^mybooks/$', UserBookList.as_view(),
            name='my-book-list'),
        re_path(r'^book-create/$',
            BookCreateView.as_view(), name='book-create'),
        re_path(r'^book-view/(?P<pk>\d+)/$',
            BookDetail.as_view(), name='book-detail'),
        re_path(r'^create-pdf/(?P<id>\d+)/$',
            CreatePDFView.as_view(), name='books-create-pdf'),
        re_path(r'^collection-view/(?P<pk>\d+)/$',
            CollectionDetail.as_view(), name='collection-detail'),
        re_path(r'^collection-create/(?P<parent>\d+)/$',
            CollectionCreateView.as_view(), name='collection-create'),
        re_path(r'^item-view/(?P<pk>\d+)/$',
            ItemDetail.as_view(), name='item-detail'),
        re_path(r'^item-retrievetext/(?P<pk>\d+)/$',
            ItemRetrieveText.as_view(), name='item-retrievetext'),
        re_path(r'^item-create/(?P<parent>\d+)/$',
            ItemCreateView.as_view(), name='item-create'),
        re_path(r'^export-gedcom/(?P<id>\d+)/$',
            ExportGEDCOMView.as_view(), name='export-gedcom'),

        #ajax
        re_path(r'^getinstances/$',
            GetInstances.as_view(),
            name="get-instances"),
        re_path(r'^getperfam/$',
            GetPersonsFamilies.as_view(),
            name="get-persons-families"),
        )

