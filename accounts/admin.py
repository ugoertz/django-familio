# -*- coding: utf8 -*-

"""Admin classes for accounts.models."""

from __future__ import unicode_literals
from __future__ import absolute_import
from django.contrib import admin

from .models import UserProfile, UserSite


class SiteInline(admin.TabularInline):
    model = UserSite
    raw_id_fields = ('site', )
    autocomplete_lookup_fields = {'fk': ('site', ), }


class UserProfileAdmin(admin.ModelAdmin):
    inlines = [SiteInline, ]
    raw_id_fields = ('person', )
    autocomplete_lookup_fields = {'fk': ('person', ), }


admin.site.register(UserProfile, UserProfileAdmin)
