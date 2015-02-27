from django.conf.urls import patterns, url

from .views import PostComment


urlpatterns = patterns('comments.views',
                       url(r'^post/$', PostComment.as_view(),
                           name='post-comment'), )


