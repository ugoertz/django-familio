# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import json

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from filebrowser.fields import FileBrowseField

from notaro.models import Note

from .managers import CurrentSiteGeoManager, GenGeoManager
from .tasks import render_map


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

        return reverse('place-detail',
                       kwargs={'pk':  self.id, })

    class Meta:
        ordering = ('title', )
        verbose_name = 'Ort'
        verbose_name_plural = 'Orte'


class CustomMapMarker(models.Model):
    custommap = models.ForeignKey('CustomMap', verbose_name="Karte")
    place = models.ForeignKey(Place, verbose_name="Ort")
    label = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=200, blank="True",
                                   verbose_name="Beschreibung")
    label_offset_x = models.FloatField(
            default=0,
            verbose_name="Positionskorrektur Label X")
    label_offset_y = models.FloatField(
            default=0,
            verbose_name="Positionskorrektur Label Y")
    style = models.CharField(max_length=400, blank=True, null=True,
            verbose_name="Stil")
    position = models.IntegerField(default=1)

    def get_description(self):
        if self.description == '-':
            return None
        if self.description:
            return self.description
        return self.place.title

    class Meta:
        ordering = ('position', )


class CustomMap(models.Model):

    # possible values of render_status
    NOTRENDERED = "NOTRENDERED" # no rendering task has been started yet
    RENDERED = "RENDERED"       # rendered map stored in rendered field
    # if rendering task currently running, then store celery task id
    # in this field

    title = models.CharField(max_length=200, blank=True, verbose_name="Titel")
    description = models.TextField(blank=True, verbose_name="Beschreibung")

    bbox = models.PolygonField(verbose_name="Begrenzung")
    markers = models.ManyToManyField(
            Place,
            blank=True,
            through=CustomMapMarker,
            verbose_name="Markierungen")

    map_style = models.CharField(
            max_length=50, blank=True, null=True,
            verbose_name="Kartenstil")

    render_status = models.CharField(default=NOTRENDERED, max_length=800)

    # Use refresh field to allow user in admin to explicitly trigger
    # a new rendering task
    refresh = models.BooleanField(default=False)

    rendered = FileBrowseField("Bilddatei", max_length=200, directory="maps/",
                               extensions=[".png", ],
                               blank=True, null=True,
                               help_text="Gerenderte Karte im png-Format")

    sites = models.ManyToManyField(Site)

    all_objects = GenGeoManager()
    objects = CurrentSiteGeoManager()

    def save(self, *args, **kwargs):
        if self.refresh:
            render_map.delay(self.id)
            self.refresh = False
        super(CustomMap, self).save(*args, **kwargs)

    def get_render_status(self):
        if self.render_status == CustomMap.RENDERED:
            return 'Aktuelle Karte ist gerendert.'
        if self.render_status == CustomMap.NOTRENDERED:
            return 'Aktuelle Karte ist noch nicht gerendert.'
        return 'Aktuelle Karte wird gerade gerendert (id %s).' % self.render_status


    def geojson(self):
        gj = {
                "type": "FeatureCollection",
                "features" :
                [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                m.place.location.x + m.label_offset_x,
                                m.place.location.y + m.label_offset_y, ]
                            },
                        "properties": {
                            "label": m.label,
                            "scale": 1.0,

                            # the following settings have no effect so far; need
                            # to wait for Mapnik 3.0
                            "font": "Open Sans Bold",
                            "font-size": 12.0,
                            "image": "circle_black.svg"
                            }
                        }
                    for m in self.custommapmarker_set.all()]
                }
        return json.dumps(gj)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('custommap-detail',
                       kwargs={'pk':  self.id, })

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Eigene Landkarte'
        verbose_name_plural = 'Eigene Landkarten'
