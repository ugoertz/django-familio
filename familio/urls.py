""" Default urlconf for familio """

from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.conf import settings
from filebrowser.sites import site
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from dajaxice.core import dajaxice_autodiscover, dajaxice_config

from base.views import CustomAutocompleteLookup
from genealogio.models import Place

admin.autodiscover()
dajaxice_autodiscover()


def bad(request):
    """ Simulates a server error """
    1 / 0


class ImpressumView(TemplateView):
    template_name = "impressum.html"

    def get_context_data(self, **kwargs):
        context = super(ImpressumView, self).get_context_data(**kwargs)
        context['staff'] = get_user_model().objects.filter(is_staff=True)
        return context


urlpatterns = patterns('',
                       url(r'^grappelli/lookup/autocomplete/$',
                           CustomAutocompleteLookup.as_view(),
                           name="grp_autocomplete_lookup"),
                       (r'^admin/filebrowser/', include(site.urls)),
                       (r'^grappelli/', include('grappelli.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       (r'^comments/', include('comments.urls')),
                       (r'^accounts/', include('accounts.urls')),
                       (r'^accounts/', include('userena.urls')),
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
                       url(r'^gen/', include('genealogio.urls')),
                       url(r'^notes/', include('notaro.urls')),
                       url(dajaxice_config.dajaxice_url,
                           include('dajaxice.urls')),
                       url(r'^' + settings.MEDIA_URL[1:] + r'(?P<fname>.*)$',
                           'base.views.download', name="download"), )\
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)), )


