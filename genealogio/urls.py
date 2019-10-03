from django.conf.urls import url

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
        url(r'^persons/$', PersonList.as_view(),
            name='person-list'),
        url(r'^persons/(?P<order_by>\w+)/$', PersonList.as_view(),
            name='person-list-ordered'),
        url(r'^person-view/(?P<pk>\d+)/$',
            PersonDetail.as_view(), name='person-detail'),
        url(r'^families/$', FamilyList.as_view(),
            name='family-list'),
        url(r'^family-view/(?P<pk>\d+)/$',
            FamilyDetail.as_view(), name='family-detail'),
        url(r'^event-view/(?P<pk>\d+)/$',
            EventDetail.as_view(), name='event-detail'),
        url(r'^pp-data.geojson$',
            PPlacesGeoJSON.as_view(),
            name='personplaces-data'),
        url(r'^data.geojson$',
            HomeGeoJSON.as_view(),
            name='data'),
        url(r'^pedigree/(?P<pk>\d+)/$', Pedigree.as_view(),
            name='pedigree'),
        url(r'^pedigree/(?P<pk>\d+)/(?P<level>\d+)/$', Pedigree.as_view(),
            name='pedigree-level'),
        url(r'^pedigree-pdf/(?P<handle>\w+)/(?P<generations>\d+)/$',
            PedigreePDF.as_view(),
            name='pedigree-pdf'),
        url(r'^descendants/(?P<pk>\d+)/$',
            Descendants.as_view(),
            name='descendants'),
        url(r'^descendants/(?P<pk>\d+)/(?P<level>\d+)/$',
            Descendants.as_view(),
            name='descendants-level'),
        url(r'^descendants-pdf/(?P<handle>\w+)/(?P<generations>\d+)/$',
            DescendantsPDF.as_view(),
            name='descendants-pdf'),
        url(r'^sparkline-person/' +
            r'(?P<pk>\d+)/(?P<fampk>\d+)/' +
            r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
            Sparkline.as_view(),
            name='sparkline-person'),
        url(r'^sparkline-head/' +
            r'(?P<fampk>\d+)/' +
            r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
            Sparkline.as_view(),
            name='sparkline-head'),
        url(r'^sparkline-tlitem/' +
            r'(?P<tlid>\d+)/' +
            r'(?P<fr>\d\d\d\d)/(?P<to>\d\d\d\d)/$',
            Sparkline.as_view(),
            name='sparkline-tlitem'),
        url(r'^add-parents/(?P<pk>\d+)/',
                AddParents.as_view(),
                name="add_parents"),
        url(r'^add-child/(?P<pk>\d+)/',
                AddChildView.as_view(),
                name="add_child"),
        url(r'^add-spouse/(?P<pk>\d+)/',
                AddSpouseView.as_view(),
                name="add_spouse"),

        # ajax
        url(r'^pplaces-lines/(?P<person_id>\d+)/$',
                PPlacesLines.as_view(),
                name="pplaces-lines"),
        url(r'^autocomplete/$',
                AutocompleteView.as_view(),
                name="autocomplete"),
        url(r'^popoverdata/$',
                PopoverData.as_view(),
                name="popover-data"),  # use when link is filled in by js
        )

