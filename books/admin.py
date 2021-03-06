# -*- coding: utf8 -*-

"""Admin classes for books.models."""

from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import (Book, Collection, Item, )


class BookAdmin(VersionAdmin):

    class Meta:
        verbose_name = 'Buch'
        verbose_name_plural = 'Bücher'


admin.site.register(Book, BookAdmin)


class CollectionAdmin(VersionAdmin):

    class Meta:
        verbose_name = 'Kollektion'
        verbose_name_plural = 'Kollektionen'


admin.site.register(Collection, CollectionAdmin)


class ItemAdmin(VersionAdmin):

    class Meta:
        verbose_name = 'Eintrag'
        verbose_name_plural = 'Einträge'


admin.site.register(Item, ItemAdmin)
