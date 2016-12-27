""" Default urlconf for familio """

from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.views.generic import TemplateView
from filebrowser.sites import site
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
import debug_toolbar

from base.views import CustomAutocompleteLookup
from accounts.models import UserSite
from genealogio.models import Place

dajaxice_autodiscover()


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


urlpatterns = patterns('',
                       url(r'^grappelli/lookup/autocomplete/$',
                           CustomAutocompleteLookup.as_view(),
                           name="grp_autocomplete_lookup"),
                       (r'^admin/filebrowser/', include(site.urls)),
                       (r'^grappelli/', include('grappelli.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       (r'^forum/', include('pybb.urls', namespace='pybb')),
                       (r'^comments/', include('comments.urls')),
                       (r'^accounts/', include('accounts.urls')),
                       (r'^accounts/', include('userena.urls')),
                       (r'^tags/', include('tags.urls')),
                       (r'^messages/',
                           include('userena.contrib.umessages.urls')),
                       url(r"^search/", include("watson.urls",
                                                namespace="watson"),
                           {'template_name': 'base/searchresults.html',
                            'paginate_by': 15,
                            'context_object_name': 'object_list',
                            'exclude': (Place, ),
                            }),
                       url(r'^bad/$', bad),
                       url(r'impressum/$',
                           ImpressumView.as_view(),
                           name='impressum'),
                       url(r'robots\.txt$',
                           TemplateView.as_view(template_name="robots.txt",
                                                content_type='plain/text')),
                       url(r'', include('base.urls')),
                       url(r'^maps/', include('maps.urls')),
                       url(r'^books/', include('books.urls')),
                       url(r'^gen/', include('genealogio.urls')),
                       url(r'^notes/', include('notaro.urls')),
                       url(dajaxice_config.dajaxice_url,
                           include('dajaxice.urls')),
                       url(r'^' + settings.MEDIA_URL[1:] + r'(?P<fname>.*)$',
                           'base.views.download', name="download"),
                       )

if settings.DEBUG:
    urlpatterns += patterns(
            '',
            url(r'^__debug__/', include(debug_toolbar.urls)),
            )

