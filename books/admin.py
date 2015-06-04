# -*- coding: utf8 -*-

"""Admin classes for books.models."""

from __future__ import unicode_literals
from __future__ import absolute_import

from django.contrib import admin

import reversion

from notaro.admin import CurrentSiteAdmin, CODEMIRROR_CSS
from .models import (Book, Collection, Item, )


class BookAdmin(reversion.VersionAdmin):

    class Meta:
        verbose_name = 'Buch'
        verbose_name_plural = 'Bücher'

admin.site.register(Book, BookAdmin)


class CollectionAdmin(reversion.VersionAdmin):

    class Meta:
        verbose_name = 'Kollektion'
        verbose_name_plural = 'Kollektionen'

admin.site.register(Collection, CollectionAdmin)


class ItemAdmin(reversion.VersionAdmin):

    class Meta:
        verbose_name = 'Eintrag'
        verbose_name_plural = 'Einträge'

admin.site.register(Item, ItemAdmin)

