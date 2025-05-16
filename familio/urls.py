""" Default urlconf for familio """

from django.urls import include, re_path
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.urls import path
from django.views.generic import TemplateView
from filebrowser.sites import site
import debug_toolbar

from base.views import CustomAutocompleteLookup, download
from accounts.models import UserSite
from genealogio.models import Place


def bad(request):
    """ Simulates a server error """
    1 / 0


class ImpressumView(TemplateView):
    template_name = "impressum.html"

    def get_context_data(self, **kwargs):
        context = super(ImpressumView, self).get_context_data(**kwargs)
        context['staff'] = get_user_model().objects.filter(
            is_active=True,
            userprofile__usersite__site=Site.objects.get_current(),
            userprofile__usersite__role__in=[UserSite.STAFF,
                                             UserSite.SUPERUSER])\
            .order_by('last_name', 'first_name').distinct()
        return context


urlpatterns = (
        re_path(r'^grappelli/lookup/autocomplete/$',
            CustomAutocompleteLookup.as_view(),
            name="grp_autocomplete_lookup"),
        path('admin/filebrowser/', site.urls),
        path('grappelli/', include('grappelli.urls')),
        path('admin/', admin.site.urls),
        re_path(r'^forum/', include('pybb.urls', namespace='pybb')),
        re_path(r'^comments/', include('comments.urls')),
        re_path(r'^accounts/', include('accounts.urls')),
        re_path(r'^accounts/', include('userena.urls')),
        re_path(r'^tags/', include('tags.urls')),
        re_path(r'^messages/',
            include('userena.contrib.umessages.urls')),
        re_path(r"^search/", include("watson.urls",
            namespace="watson"),
            {'template_name': 'base/searchresults.html',
                'paginate_by': 15,
                'context_object_name': 'object_list',
                'exclude': (Place, ),
             }),
        re_path(r'^bad/$', bad),
        re_path(r'impressum/$',
            ImpressumView.as_view(),
            name='impressum'),
        re_path(r'robots\.txt$',
            TemplateView.as_view(template_name="robots.txt",
                                 content_type='plain/text')),
        re_path(r'', include('base.urls')),
        re_path(r'^maps/', include('maps.urls')),
        re_path(r'^books/', include('books.urls')),
        re_path(r'^gen/', include('genealogio.urls')),
        re_path(r'^notes/', include('notaro.urls')),
        re_path(r'^' + settings.MEDIA_URL[1:] + r'(?P<fname>.*)$',
            download, name="download"),
        )

if settings.DEBUG:
    urlpatterns += (
            re_path(r'^__debug__/', include(debug_toolbar.urls)),
            )
