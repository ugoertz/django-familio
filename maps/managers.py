# -*- coding: utf8 -*-


# Still needed since CurrentSiteGeoManager is imported in migration 0010 ...
# Can be deleted once this has been applied "everywhere".

from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.gis.db.models import GeoManager


class GenGeoManager(GeoManager):

    def on_site(self):
        return self.filter(sites=Site.objects.get_current())


class CurrentSiteGeoManager(CurrentSiteManager, GeoManager):
    use_for_related_fields = True

