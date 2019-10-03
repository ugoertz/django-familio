# -*- coding: utf8 -*-

"""Admin classes for tags.models."""

from django.contrib import admin

from .models import CustomTag


class CustomTagAdmin(admin.ModelAdmin):
    pass


admin.site.register(CustomTag, CustomTagAdmin)
