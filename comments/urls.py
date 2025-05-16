from django.urls import re_path

from .views import PostComment


urlpatterns = (
        re_path(r'^post/$', PostComment.as_view(),
            name='post-comment'),
        )


