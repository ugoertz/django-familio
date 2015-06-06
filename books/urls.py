from django.conf.urls import patterns, url

from .views import (
        PublicBookList, UserBookList,
        BookCreateView, BookDetail, CreatePDFView,
        CollectionDetail, CollectionCreateView,
        ItemDetail, ItemCreateView, ItemRetrieveText
        )


urlpatterns = patterns('books.views',
        url(r'^publicbooks/$', PublicBookList.as_view(),
            name='public-book-list'),
        url(r'^mybooks/$', UserBookList.as_view(),
            name='my-book-list'),
        url(r'^book-create/$',
            BookCreateView.as_view(), name='book-create'),
        url(r'^book-view/(?P<pk>\d+)/$',
            BookDetail.as_view(), name='book-detail'),
        url(r'^create-pdf/(?P<id>\d+)/$',
            CreatePDFView.as_view(), name='books-create-pdf'),
        url(r'^collection-view/(?P<pk>\d+)/$',
            CollectionDetail.as_view(), name='collection-detail'),
        url(r'^collection-create/(?P<parent>\d+)/$',
            CollectionCreateView.as_view(), name='collection-create'),
        url(r'^item-view/(?P<pk>\d+)/$',
            ItemDetail.as_view(), name='item-detail'),
        url(r'^item-retrievetext/(?P<pk>\d+)/$',
            ItemRetrieveText.as_view(), name='item-retrievetext'),
        url(r'^item-create/(?P<parent>\d+)/$',
            ItemCreateView.as_view(), name='item-create'),
        )

