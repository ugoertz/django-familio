# -*- coding: utf8 -*-

"""Admin classes for tags.models."""

from __future__ import unicode_literals
from __future__ import absolute_import
from django.contrib import admin

from .models import CustomTag


class CustomTagAdmin(admin.ModelAdmin):
    pass


admin.site.register(CustomTag, CustomTagAdmin)
