# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.db import models


class GenManager(models.Manager):

    def on_site(self):
        return self.filter(sites=Site.objects.get_current())

