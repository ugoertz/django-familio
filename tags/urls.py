from django.urls import re_path

from .views import TagSearch, SaveTags, TagList
from .ajax import GetTags

urlpatterns = (
    re_path(r'^save-tags/(?P<app>\w+)/(?P<model>\w+)/(?P<pk>\d+)/$',
        SaveTags.as_view(), name='save-tags'),
    re_path(r'^tag-search/(?P<tag>[\w !:\.,;_+-]+)/$',
        TagSearch.as_view(), name='tag-search'),
    re_path(r'^tag-list/$',
        TagList.as_view(), name='tag-list'),

    # ajax
    re_path(r'^get-tags/$', GetTags.as_view(), name="get-tags"),
    )

