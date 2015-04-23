from django.conf.urls import patterns, url

from .views import NoteDetail, NoteList, PictureDetail, SourceDetail


urlpatterns = patterns('notaro.views',
                       url(r'^all/$', NoteList.as_view(),
                           name='note-list'),
                       url(r'^source-view/(?P<pk>\d+)/$',
                           SourceDetail.as_view(), name='source-detail'),
                       url(r'^note-view/(?P<pk>\d+)/$',
                           NoteDetail.as_view(), name='note-detail'),
                       url(r'^picture-view/(?P<pk>\d+)/$',
                           PictureDetail.as_view(), name='picture-detail'), )


