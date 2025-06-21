# -*- coding: utf8 -*-

"""Admin classes for books.models."""

from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import FamilyTree


class FTAdmin(VersionAdmin):

    class Meta:
        verbose_name = 'Stammbaum'
        verbose_name_plural = 'Stammbäume'


admin.site.register(FamilyTree, FTAdmin)
