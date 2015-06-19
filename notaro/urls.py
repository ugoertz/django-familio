from django.conf.urls import patterns, url

from .views import (
        NoteDetail, NoteList, PictureDetail, PictureList,
        SourceDetail,
        DocumentList, DocumentDetail, SourceList,
        )


urlpatterns = patterns('notaro.views',
                       url(r'^all/$', NoteList.as_view(),
                           name='note-list'),
                       url(r'^sources/$', SourceList.as_view(),
                           name='source-list'),
                       url(r'^docs/$', DocumentList.as_view(),
                           name='document-list'),
                       url(r'^source-view/(?P<pk>\d+)/$',
                           SourceDetail.as_view(), name='source-detail'),
                       url(r'^note-view/(?P<pk>\d+)/$',
                           NoteDetail.as_view(), name='note-detail'),
                       url(r'^doc-view/(?P<pk>\d+)/$',
                           DocumentDetail.as_view(), name='document-detail'),
                       url(r'^picture-view/(?P<pk>\d+)/$',
                           PictureDetail.as_view(), name='picture-detail'),
                       url(r'^picture-list/$',
                           PictureList.as_view(), name='picture-list'),
                       url(r'^picture-list/(?P<size>\w+)/$',
                           PictureList.as_view(), name='picture-list'),
                       )


