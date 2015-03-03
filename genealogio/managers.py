# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.gis.db.models import GeoManager


class CurrentSiteGeoManager(CurrentSiteManager, GeoManager):
    use_for_related_fields = True


