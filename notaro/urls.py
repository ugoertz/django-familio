from django.conf.urls import url

from .views import (
        NoteDetail, NoteList, PictureDetail, PictureList,
        VideoDetail, VideoList,
        SourceDetail,
        DocumentList, DocumentDetail, SourceList,
        UnboundImagesView, CreateThumbnail,
        SetDateFromEXIF,
        SearchForDateRange,
        )


urlpatterns = (
        url(r'^all/$', NoteList.as_view(),
            name='note-list'),
        url(r'^sources/$', SourceList.as_view(),
            name='source-list'),
        url(r'^docs/$', DocumentList.as_view(),
            name='document-list'),
        url(r'^docs/(?P<order_by>\w+)/$',
            DocumentList.as_view(),
            name='document-list-ordered'),
        url(r'^source-view/(?P<pk>\d+)/$',
            SourceDetail.as_view(), name='source-detail'),
        url(r'^note-view/(?P<pk>\d+)/$',
            NoteDetail.as_view(), name='note-detail'),
        url(r'^doc-view/(?P<pk>\d+)/$',
            DocumentDetail.as_view(), name='document-detail'),
        url(r'^picture-view/(?P<pk>\d+)/$',
            PictureDetail.as_view(), name='picture-detail'),
        url(r'^video-view/(?P<pk>\d+)/$',
            VideoDetail.as_view(), name='video-detail'),
        url(r'^unbound-images/$',
            UnboundImagesView.as_view(), name='unbound-images'),
        url(r'^video-list/$',
            VideoList.as_view(), name='video-list'),
        url(r'^picture-list/$',
            PictureList.as_view(), name='picture-list'),
        url(r'^picture-list/(?P<size>\w+)/$',
            PictureList.as_view(), name='picture-list'),
        url(r'^create-thumbnail/$',
            CreateThumbnail.as_view(),
            name='document-thumbnail'),
        url(r'^date-from-exif/(?P<pk>\d+)/$',
            SetDateFromEXIF.as_view(),
            name='set-date-from-exif'),
        url(r'^date-range/$',
            SearchForDateRange.as_view(),
            name='date-range'),
        url(r'^date-range/(?P<fr>\d+)/(?P<to>\d+)/' +
            r'(?P<undated>[YN])/$',
            SearchForDateRange.as_view(),
            name='date-range'),
        )


