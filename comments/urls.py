from django.conf.urls import url

from .views import PostComment


urlpatterns = (
        url(r'^post/$', PostComment.as_view(),
            name='post-comment'),
        )


