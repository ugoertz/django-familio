from django.conf.urls import patterns, url

from .views import TagSearch, SaveTags, TagList

urlpatterns = patterns(
    'tags.views',
    url(r'^save-tags/(?P<app>\w+)/(?P<model>\w+)/(?P<pk>\d+)/$',
        SaveTags.as_view(), name='save-tags'),
    url(r'^tag-search/(?P<tag>[\w !:\.,;_+-]+)/$',
        TagSearch.as_view(), name='tag-search'),
    url(r'^tag-list/$',
        TagList.as_view(), name='tag-list'),
    )

