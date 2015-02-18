from django.conf.urls import patterns, url

from .views import NoteDetail, NoteList


urlpatterns = patterns('notaro.views',
                       url(r'^all/$', NoteList.as_view(),
                           name='note-list'),
                       url(r'^note-view/(?P<pk>\d+)/$',
                           NoteDetail.as_view(), name='note-detail'), )

