# -*- coding: utf8 -*-

"""Admin classes for base.models."""

from django.contrib import admin

from .models import SiteProfile


class SiteProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('site', 'neighbor_sites', )
    autocomplete_lookup_fields = {
            'fk': ['site', ],
            'm2m': ['neighbor_sites', ], }


admin.site.register(SiteProfile, SiteProfileAdmin)

