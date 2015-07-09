# -*- coding: utf8 -*-

from __future__ import unicode_literals

import os
import os.path
import re

from django.db import models
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.managers import CurrentSiteManager
from filebrowser.fields import FileBrowseField
from filebrowser.settings import ADMIN_THUMBNAIL
from taggit.managers import TaggableManager

from .managers import GenManager
from tags.models import CustomTagThrough


class Source(models.Model):
    UNKNOWN = 0
    DOUBTFUL = 1
    UNCERTAIN = 2
    CERTAIN = 3
    VERYCERTAIN = 4

    CONFIDENCE_TYPE = ((UNKNOWN, 'unbekannt'),
                       (DOUBTFUL, 'zweifelhaft'),
                       (UNCERTAIN, 'unsicher'),
                       (CERTAIN, 'sicher'),
                       (VERYCERTAIN, 'sehr sicher'), )

    # OTHER = 5
    # AUDIO = 6
    # BOOK = 7
    # CARD = 8
    # ELECTRONIC = 9
    # FICHE = 10
    # FILM = 11
    # MAGAZINE = 12
    # MANUSCRIPT = 13
    # MAP = 14
    # NEWSPAPER = 15
    # PHOTO = 16
    # TOMBSTONE = 17
    # VIDEO = 18

    # SOURCE_MEDIA_TYPE = ((UNKNOWN, 'Unknown'),
    #                      (OTHER, 'Custom'),
    #                      (AUDIO, 'Audio'),
    #                      (BOOK, 'Book'),
    #                      (CARD, 'Card'),
    #                      (ELECTRONIC, 'Electronic'),
    #                      (FICHE, 'Fiche'),
    #                      (FILM, 'Film'),
    #                      (MAGAZINE, 'Magazine'),
    #                      (MANUSCRIPT, 'Manuscript'),
    #                      (MAP, 'Map'),
    #                      (NEWSPAPER, 'Newspaper'),
    #                      (PHOTO, 'Photo'),
    #                      (TOMBSTONE, 'Tombstone'),
    #                      (VIDEO, 'Video'), )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, verbose_name="Beschreibung")
    confidence_level = models.IntegerField(choices=CONFIDENCE_TYPE,
                                           default=UNKNOWN,
                                           verbose_name="Zuverlässigkeit"
                                           )
    # media_type = models.IntegerField(choices=SOURCE_MEDIA_TYPE,
    #                                  default=UNKNOWN)
    documents = models.ManyToManyField(
            'Document',
            verbose_name="Dokumente",
            blank=True
            )

    sites = models.ManyToManyField(Site)
    all_objects = GenManager()
    objects = CurrentSiteManager()

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("name__icontains", )

    def on_current_site(self):
        return Site.objects.get_current() in self.sites.all()

    def related_label(self):
        if Site.objects.get_current() in self.sites.all():
            return self.__unicode__()
        else:
            return '[[ %s ]]' % self.__unicode__()

    def get_absolute_url(self):
        return reverse('source-detail', kwargs={'pk': self.id, })

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )
        verbose_name = 'Quelle'
        verbose_name_plural = 'Quellen'


class PictureSource(models.Model):
    picture = models.ForeignKey('Picture', verbose_name="Bild")
    source = models.ForeignKey(Source, verbose_name="Quelle")
    comment = models.CharField(max_length=500, blank=True, verbose_name="Kommentar")


class Picture(models.Model):
    image = FileBrowseField("Bilddatei", max_length=200, directory="images/",
                            extensions=[".jpg", ".png", ],
                            blank=True, null=True,
                            help_text="Bilddatei im jpg- oder png-Format")
    caption = models.TextField(blank=True, verbose_name='Beschreibung')
    date = models.DateField(blank=True, null=True, verbose_name='Datum')
    sources = models.ManyToManyField(Source, blank=True,
                                     verbose_name="Quellen",
                                     through=PictureSource)

    sites = models.ManyToManyField(Site)
    all_objects = GenManager()
    objects = CurrentSiteManager()
    tags = TaggableManager(
            through=CustomTagThrough,
            blank=True, help_text="")

    def __unicode__(self):
        # pylint: disable=no-member
        return '[%d] %s <img src="%s">' %\
               (self.id,
                self.caption[:25] or self.image.original_filename,
                self.image.version_generate(ADMIN_THUMBNAIL).url)

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("id__iexact", "caption__icontains",
                "image__icontains", )

    def related_label(self):
        if Site.objects.get_current() in self.sites.all():
            return self.__unicode__()
        else:
            return '[[ %s ]]' % self.__unicode__()

    def get_absolute_url(self):
        return reverse('picture-detail', kwargs={'pk': self.id, })

    def as_html_in_list(self):
        """
        HTML representing this picture (typically to be used to show a list of
        pictures with a certain tag, e.g. in a detail view of a Person, ...
        """

        # pylint: disable=no-member
        return '<img src="%s">' % self.image.version_generate('small').url

    def get_caption(self):
        return self.caption
        # return '\n'.join(['.. class:: cabin\n\n'] +
        #                  ['    '+l for l in self.caption.splitlines()])

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Bild'
        verbose_name_plural = 'Bilder'


class Document(models.Model):
    doc = FileBrowseField("Document", max_length=200, directory="documents/",
                          extensions=[".pdf", ".doc", ".docx", ".rtf", ".jpg",
                                      ".tif", ".mp3", ".mp4", ],
                          blank=True, null=True,
                          help_text=".pdf, .doc, .rtf, .jpg, .tif, .mp3, .mp4")
    name = models.CharField(max_length=500, verbose_name="Name")
    description = models.TextField(blank=True, verbose_name="Beschreibung")
    date = models.DateField(blank=True, null=True, verbose_name="Datum")
    sites = models.ManyToManyField(Site)
    all_objects = GenManager()
    objects = CurrentSiteManager()
    tags = TaggableManager(
            through=CustomTagThrough,
            blank=True, help_text="")

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("name_icontains", "description__icontains", )

    def related_label(self):
        if Site.objects.get_current() in self.sites.all():
            return self.__unicode__()
        else:
            return '[[ %s ]]' % self.__unicode__()

    def as_html_in_list(self):
        """
        HTML representing this document (typically to be used to show a list of
        objects with a certain tag, e.g. in a detail view of a Person, ...
        """

        # pylint: disable=no-member
        return '<li class="list-group-item" style="font-size: 140%%;">%s<br><span style="font-family: courier, monospace; font-size: 70%%">%s, Objekt-ID: %d</span></li>' % (
                self.name, os.path.basename(self.doc.filename), self.id)

    def __unicode__(self):
        # pylint: disable=no-member
        return '%d: %s' % (self.id, self.name)

    def get_absolute_url(self):
        return reverse('document-detail', kwargs={'pk': self.pk, })

    class Meta:
        ordering = ('date', )
        verbose_name = 'Dokument'
        verbose_name_plural = 'Dokumente'


class PictureNote(models.Model):
    note = models.ForeignKey('Note', verbose_name="Text")
    picture = models.ForeignKey(Picture, verbose_name="Bild")
    position = models.IntegerField(default=1)

    class Meta:
        ordering = ('position', )


class NoteSource(models.Model):
    note = models.ForeignKey('Note', verbose_name="Text")
    source = models.ForeignKey(Source, verbose_name="Quelle")
    comment = models.CharField(max_length=500, blank=True, verbose_name="Kommentar")


class Note(models.Model):

    title = models.CharField(max_length=200, verbose_name='Titel')
    link = models.CharField(max_length=50, unique=True)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)

    published = models.BooleanField(default=True,
                                    verbose_name='Veröffentlicht?')
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                     verbose_name='Autoren')

    pictures = models.ManyToManyField('Picture', blank=True,
                                      through=PictureNote,
                                      verbose_name='Bilder')
    sources = models.ManyToManyField(Source, blank=True,
                                     verbose_name="Quellen",
                                     through=NoteSource)

    sites = models.ManyToManyField(Site)
    all_objects = GenManager()
    objects = CurrentSiteManager()

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("title__icontains", "link__icontains", )

    def get_pictures(self):
        """Return all pictures attached to note which are available on current
        site, ordered by PictureNote.position."""

        # pylint: disable=no-member
        return self.pictures.on_site().order_by('picturenote__position')

    def get_trailer(self):
        """Return the 'first section' of self.text. This means either

        - everything until a comment ".. end_trailer\n" is encountered, or
        - everything until the first "\n\n" at least 200 characters into the
          file is encountered.
        """

        end_trailer = self.text.find(".. end_trailer")
        if end_trailer == -1:
            end_trailer = self.text.find("\r\n\r\n", 50)
        if end_trailer == -1:
            end_trailer = self.text.find("\n\n", 50)

        if end_trailer == -1 or end_trailer >= 700:
            return self.text[:700]
        trailer = self.text[:end_trailer].rstrip() +\
            (' ...' if end_trailer < len(self.text) else '')
        trailer = re.sub(r'-{4,}', lambda m: '`'*len(m.group(0)), trailer)
        return trailer

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(Note, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.link:
            return '/n' + self.link
        else:
            return reverse('note-detail', kwargs={'pk': self.id, })

    def related_label(self):
        if Site.objects.get_current() in self.sites.all():
            return self.__unicode__()
        else:
            return '[[ %s ]]' % self.__unicode__()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('title', )
        verbose_name = 'Text'
        verbose_name_plural = 'Texte'
