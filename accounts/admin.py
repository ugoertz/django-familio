# -*- coding: utf8 -*-

"""Admin classes for accounts.models."""

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
    list_display = ('user', 'is_active_user', 'person', 'sites_staff', 'sites_user')

    def sites_staff(self, obj):
        return ', '.join([s.siteprofile.short_name for s in obj.sites.filter(
            usersite__role__in=[UserSite.STAFF, UserSite.SUPERUSER])])

    def sites_user(self, obj):
        return ', '.join([s.siteprofile.short_name for s in 
            obj.sites.filter(usersite__role=UserSite.USER)])

    def is_active_user(self, obj):
        return obj.user.is_active
    is_active_user.boolean = True
    is_active_user.short_description = 'Aktiviert?'


admin.site.register(UserProfile, UserProfileAdmin)
