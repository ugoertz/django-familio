# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from notaro.models import Note

from .managers import CurrentSiteGeoManager, GenGeoManager


def cleanname(name):
    """Replace umlauts (ä by ae, etc.) and then remove all non-ASCII letters
    from string."""

    for umlaut, expansion in [('Ä', 'Ae'), ('Ö', 'Oe'), ('Ü', 'Ue'),
                              ('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'),
                              ('ß', 'ss'), ]:
        name = name.replace(umlaut, expansion)
    return u''.join([c for c in name
                     if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
                     'abcdefghijklmnopqrstuvwxyz'])


class Url(models.Model):
    title = models.CharField(max_length=200, blank=True)
    link = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title or self.link[:50]

    def related_label(self):
        return '<a href="%s">%s</a>' %\
               (self.link, self.title or self.link[:50], )


class PlaceUrl(models.Model):
    url = models.ForeignKey(Url)
    place = models.ForeignKey('Place')
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ('position', )
        verbose_name = 'URL zum Ort'
        verbose_name_plural = 'URLs zum Ort'


class PlaceNote(models.Model):
    place = models.ForeignKey('Place')
    note = models.ForeignKey(Note)
    position = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Text zu Ort'
        verbose_name_plural = 'Texte zu Ort'


class Place(models.Model):
    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(blank=True)
    handle = models.CharField(max_length=50, unique=True)

    urls = models.ManyToManyField(Url, through=PlaceUrl, blank=True)
    location = models.PointField(blank=True, null=True)

    notes = models.ManyToManyField(Note, blank=True, through=PlaceNote)

    objects = models.GeoManager()

    def reset_handle(self):
        """Recompute handle for a Place object which already has an id."""

        self.handle = 'L_'
        if self.title:
            self.handle += cleanname(self.title)[:20]
        if self.location:
            # pylint: disable=no-member
            self.handle += str(self.location.x)[:10] + '_'
            self.handle += str(self.location.y)[:10]

        self.handle += '-' + unicode(self.id)
        self.handle = self.handle[:49]
        self.save()

    def __unicode__(self):
        return self.title

    def related_label(self):
        return self.__unicode__()

    @staticmethod
    def autocomplete_search_fields():
        return ("title__startswith",)

    def get_absolute_url(self):
        """Return URL where this object can be viewed."""

        return reverse('%s-detail' % self.__class__.__name__.lower(),
                       kwargs={'pk':  self.id, })

    class Meta:
        ordering = ('title', )
        verbose_name = 'Ort'
        verbose_name_plural = 'Orte'



