from django.urls import re_path

from .views import (
        PersonList, PersonDetail, EventDetail, FamilyList,
        Sparkline,
        Pedigree, PedigreePDF,
        Descendants, DescendantsPDF,
        HomeGeoJSON, FamilyDetail, PPlacesGeoJSON,
        AddParents, AddChildView, AddSpouseView,
        )
from .ajax import (
        PPlacesLines, AutocompleteView, PopoverData,
        )


urlpatterns = (
        re_path(r'^persons/$', PersonList.as_view(),
            name='person-list'),
        re_path(r'^persons/(?P<order_by>\w+)/$', PersonList.as_view(),
            name='person-list-ordered'),
        re_path(r'^person-view/(?P<pk>\d+)/$',
            PersonDetail.as_view(), name='person-detail'),
        re_path(r'^families/$', FamilyList.as_view(),
            name='family-list'),
        re_path(r'^family-view/(?P<pk>\d+)/$',
            FamilyDetail.as_view(), name='family-detail'),
        re_path(r'^event-view/(?P<pk>\d+)/$',
            EventDetail.as_view(), name='event-detail'),
        re_path(r'^pp-data.geojson$',
            PPlacesGeoJSON.as_view(),
            name='personplaces-data'),
        re_path(r'^data.geojson$',
            HomeGeoJSON.as_view(),
            name='data'),
        re_path(r'^pedigree/(?P<pk>\d+)/$', Pedigree.as_view(),
            name='pedigree'),
        re_path(r'^pedigree/(?P<pk>\d+)/(?P<level>\d+)/$', Pedigree.as_view(),
            name='pedigree-level'),
        re_path(r'^pedigree-pdf/(?P<handle>\w+)/(?P<generations>\d+)/$',
            PedigreePDF.as_view(),
            name='pedigree-pdf'),
        re_path(r'^descendants/(?P<pk>\d+)/$',
            Descendants.as_view(),
            name='descendants'),
        re_path(r'^descendants/(?P<pk>\d+)/(?P<level>\d+)/$',
            Descendants.as_view(),
            name='descendants-level'),
        re_path(r'^descendants-pdf/(?P<handle>\w+)/(?P<generations>\d+)/$',
            DescendantsPDF.as_view(),
            name='descendants-pdf'),
        re_path(r'^sparkline-person/' +
            r'(?P<pk>\d+)/(?P<fampk>\d+)/' +
            r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
            Sparkline.as_view(),
            name='sparkline-person'),
        re_path(r'^sparkline-head/' +
            r'(?P<fampk>\d+)/' +
            r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
            Sparkline.as_view(),
            name='sparkline-head'),
        re_path(r'^sparkline-tlitem/' +
            r'(?P<tlid>\d+)/' +
            r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
            Sparkline.as_view(),
            name='sparkline-tlitem'),
        re_path(r'^add-parents/(?P<pk>\d+)/',
                AddParents.as_view(),
                name="add_parents"),
        re_path(r'^add-child/(?P<pk>\d+)/',
                AddChildView.as_view(),
                name="add_child"),
        re_path(r'^add-spouse/(?P<pk>\d+)/',
                AddSpouseView.as_view(),
                name="add_spouse"),

        # ajax
        re_path(r'^pplaces-lines/(?P<person_id>\d+)/$',
                PPlacesLines.as_view(),
                name="pplaces-lines"),
        re_path(r'^autocomplete/$',
                AutocompleteView.as_view(),
                name="autocomplete"),
        re_path(r'^popoverdata/$',
                PopoverData.as_view(),
                name="popover-data"),  # use when link is filled in by js
        )

