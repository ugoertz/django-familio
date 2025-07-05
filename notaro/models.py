# -*- coding: utf8 -*-

import os
import os.path
import re
import tempfile
from PIL import ExifTags, Image

from django.db import models
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.html import escape
from django.utils.safestring import mark_safe
from filebrowser.fields import FileBrowseField
from filebrowser.settings import ADMIN_THUMBNAIL
from taggit.managers import TaggableManager

from partialdate.fields import PartialDateField
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
            return self.__str__()
        else:
            return '[[ %s ]]' % self.__str__()

    def get_absolute_url(self):
        return reverse('source-detail', kwargs={'pk': self.id, })

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )
        verbose_name = 'Quelle'
        verbose_name_plural = 'Quellen'


class PictureSource(models.Model):
    picture = models.ForeignKey(
            'Picture',
            verbose_name="Bild",
            on_delete=models.CASCADE)
    source = models.ForeignKey(
            Source,
            verbose_name="Quelle",
            on_delete=models.CASCADE)
    comment = models.CharField(
            max_length=500,
            blank=True,
            verbose_name="Kommentar")


class Picture(models.Model):
    image = FileBrowseField("Bilddatei", max_length=200, directory="images/",
                            extensions=[".jpg", ".png", ],
                            blank=True, null=True,
                            help_text="Bilddatei im jpg- oder png-Format")
    caption = models.TextField(blank=True, verbose_name='Beschreibung')
    date = PartialDateField(blank=True, default='', verbose_name='Datum')
    sources = models.ManyToManyField(Source, blank=True,
                                     verbose_name="Quellen",
                                     through=PictureSource)

    sites = models.ManyToManyField(Site)
    all_objects = GenManager()
    objects = CurrentSiteManager()
    tags = TaggableManager(
            through=CustomTagThrough,
            blank=True, help_text="")

    def __str__(self):
        # pylint: disable=no-member
        return self.caption[:25] or self.image.original_filename

    def display_as_search_result(self):
        short_caption = self.caption[:100]
        if len(self.caption) > 100:
            short_caption += '...'
        return mark_safe('<img style="margin-right: 20px;" src="%s"> %s' % (
            self.image.version_generate(ADMIN_THUMBNAIL).url,
            escape(short_caption or self.image.original_filename),
        ))

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("id__iexact", "caption__icontains",
                "image__icontains", )

    def related_label(self):
        if Site.objects.get_current() in self.sites.all():
            return self.__str__()
        else:
            return '[[ %s ]]' % self.__str__()

    def get_absolute_url(self):
        return reverse('picture-detail', kwargs={'pk': self.id, })

    def as_html_in_list(self):
        """
        HTML representing this picture (typically to be used to show a list of
        pictures with a certain tag, e.g. in a detail view of a Person, ...
        """

        # pylint: disable=no-member
        if self.date:
            return '<div style="position: relative;"><img src="%s"><div class="cabin img-rounded" style="font-size: 80%%; font-weight: bold; box-sizing: border-box; position: absolute; right: 2px; bottom: 2px; background: rgba(255, 255, 255, 0.85); color: black; padding: 2px;">%d</div></div>' % (self.image.version_generate('small').url, self.date.year, )
        else:
            return '<img src="%s">' % (self.image.version_generate('small').url, )

    def get_caption(self):
        return self.caption
        # return '\n'.join(['.. class:: cabin\n\n'] +
        #                  ['    '+l for l in self.caption.splitlines()])

    def get_exif_data(self):
        try:
            p = Image.open(self.image.path_full)
            raw_exif = p._getexif()
            exif = {ExifTags.TAGS.get(k, k): raw_exif[k] for k in raw_exif}
            result = [exif.get(k, '')
                    for k in ['DateTimeOriginal', 'Make', 'Model', ]]
            if ((result[0] == '' or result[0].startswith('0000')) and
                    'DateTime' in exif):
                result[0] = exif.get('DateTime', '')
            return result
        except:
            return ['Keine EXIF-Daten gefunden.', ]

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Bild'
        verbose_name_plural = 'Bilder'


class VideoSource(models.Model):
    video = models.ForeignKey(
            'Video',
            verbose_name="Video",
            on_delete=models.CASCADE)
    source = models.ForeignKey(
            Source,
            verbose_name="Quelle",
            on_delete=models.CASCADE)
    comment = models.CharField(
            max_length=500,
            blank=True,
            verbose_name="Kommentar")


class Video(models.Model):
    video = FileBrowseField("Videodatei", max_length=200, directory="videos/",
                            extensions=[".mp4", ".ogv", ".webm", ".vob", ],
                            blank=True, null=True,
                            help_text="Videodatei, " +
                            "Formate: mp4, ogv, webm, vob.")
    poster = FileBrowseField("Bilddatei", max_length=200, directory="videos/",
                             extensions=[".jpg", ".png", ],
                             blank=True, null=True,
                             help_text="Angezeigte Bilddatei (.jpg/.png)")

    # directory where the versions of the video are stored
    directory = models.CharField(max_length=300, blank=True)

    caption = models.TextField(blank=True, verbose_name='Beschreibung')
    date = PartialDateField(blank=True, default='', verbose_name='Datum')
    sources = models.ManyToManyField(Source, blank=True,
                                     verbose_name="Quellen",
                                     through=VideoSource)

    sites = models.ManyToManyField(Site)
    all_objects = GenManager()
    objects = CurrentSiteManager()
    tags = TaggableManager(
            through=CustomTagThrough,
            blank=True, help_text="")

    def save(self, *args, **kwargs):
        ctr = 0
        while ctr < 5 and not self.directory:
            ctr += 1
            if not os.path.exists(os.path.join(
                    settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY,
                    'videos')):
                os.makedirs(os.path.join(
                    settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY,
                    'videos'))
            tmpdir = tempfile.mkdtemp(
                    dir=os.path.join(
                        settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY,
                        'videos'),
                    prefix=self.video.original_filename + '-')
            os.chmod(tmpdir, 0o775)
            self.directory = os.path.basename(tmpdir)
            # print('self.directory', self.directory)
        if not self.directory:
            # something went wrong
            raise Exception

        # pylint: disable=no-member
        super(Video, self).save(*args, **kwargs)

    def __str__(self):
        return '[%d] %s' %\
            (self.id, self.caption[:25] or self.video.original_filename)

    def display_as_search_result(self):
        if self.poster:
            return mark_safe('<img style="margin-right: 20px;" src="%s"> %s' % (
                self.poster.version_generate(ADMIN_THUMBNAIL).url,
                escape(self.caption[:100] or self.video.original_filename),
            ))
        else:
            return 'Video: [%d] %s' %\
                (self.id, self.caption[:100] or self.video.original_filename)

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("id__iexact", "caption__icontains",
                "video__icontains", )

    def related_label(self):
        if Site.objects.get_current() in self.sites.all():
            return self.__str__()
        else:
            return '[[ %s ]]' % self.__str__()

    def get_absolute_url(self):
        return reverse('video-detail', kwargs={'pk': self.id, })

    def as_html_in_list(self):
        """
        HTML representing this picture (typically to be used to show a list of
        pictures with a certain tag, e.g. in a detail view of a Person, ...
        """

        # pylint: disable=no-member
        return '<img src="%s">' % self.poster.version_generate('small').url

    def get_caption(self):
        return self.caption
        # return '\n'.join(['.. class:: cabin\n\n'] +
        #                  ['    '+l for l in self.caption.splitlines()])

    def get_mp4_size(self):
        try:
            sz = os.path.getsize(os.path.join(
                settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY,
                'videos/{dir}/video.mp4'.format(dir=self.directory)))
            return (sz // 100000) / 10.0
        except OSError:
            return None

    def get_ogv_size(self):
        try:
            sz = os.path.getsize(os.path.join(
                settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY,
                'videos/{dir}/video.ogv'.format(dir=self.directory)))
            return (sz // 100000) / 10.0
        except OSError:
            return None

    def get_webm_size(self):
        try:
            sz = os.path.getsize(os.path.join(
                settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY,
                'videos/{dir}/video.webm'.format(dir=self.directory)))
            return (sz // 100000) / 10.0
        except OSError:
            return None

    def get_mp4_url(self):
        f = os.path.join(
                settings.FILEBROWSER_DIRECTORY,
                'videos/{dir}/video.mp4'.format(dir=self.directory))
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, f)):
            return os.path.join(settings.MEDIA_URL, f)
        return None

    def get_ogv_url(self):
        f = os.path.join(
                settings.FILEBROWSER_DIRECTORY,
                'videos/{dir}/video.ogv'.format(dir=self.directory))
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, f)):
            return os.path.join(settings.MEDIA_URL, f)
        return None

    def get_webm_url(self):
        f = os.path.join(
                settings.FILEBROWSER_DIRECTORY,
                'videos/{dir}/video.webm'.format(dir=self.directory))
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, f)):
            return os.path.join(settings.MEDIA_URL, f)
        return None

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'


class Document(models.Model):
    doc = FileBrowseField(
            "Document", max_length=200, directory="documents/",
            extensions=[".pdf", ".doc", ".docx", ".rtf", ".jpg",
                        ".png", ".tif", ".mp3", ".mp4", ],
            blank=True, null=True,
            help_text=".pdf, .doc(x), .odt, .rtf, .jpg, .png, .tif, .mp3/4")
    image = FileBrowseField(
            "Bilddatei", max_length=200,
            directory="documents/",
            extensions=[".jpg", ".png", ],
            blank=True, null=True,
            help_text="Bilddatei im jpg- oder png-Format")
    name = models.CharField(max_length=500, verbose_name="Name")
    description = models.TextField(blank=True, verbose_name="Beschreibung")
    date = PartialDateField(blank=True, default='', verbose_name="Datum")
    sites = models.ManyToManyField(Site)
    date_added = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)
    all_objects = GenManager()
    objects = CurrentSiteManager()
    tags = TaggableManager(
            through=CustomTagThrough,
            blank=True, help_text="")

    @staticmethod
    def autocomplete_search_fields():
        """Used by grappelli."""
        return ("name__icontains", "description__icontains", )

    def related_label(self):
        if Site.objects.get_current() in self.sites.all():
            return self.__str__()
        else:
            return '[[ %s ]]' % self.__str__()

    def as_html_in_list(self):
        """
        HTML representing this document (typically to be used to show a list of
        objects with a certain tag, e.g. in a detail view of a Person, ...
        """

        # pylint: disable=no-member
        return ''.join([
            '<li class="list-group-item clearfix" style="font-size: 130%;">',
            ('<img src="%s" style="float:left; margin-right: 20px;">'
                % self.image.version_generate('thumbnail').url)
            if self.image else '',
            '%s<br>' % self.name,
            '<span style="font-family: courier, monospace; font-size: 70%">',
            '%s, Objekt-ID: %d</span></li>' % (
                os.path.basename(self.doc.filename), self.id), ])

    def __str__(self):
        # pylint: disable=no-member
        return self.name

    def get_absolute_url(self):
        return reverse('document-detail', kwargs={'pk': self.pk, })

    class Meta:
        ordering = ('date', )
        verbose_name = 'Dokument'
        verbose_name_plural = 'Dokumente'


class PictureNote(models.Model):
    note = models.ForeignKey(
            'Note',
            verbose_name="Text",
            on_delete=models.CASCADE)
    picture = models.ForeignKey(
            Picture,
            verbose_name="Bild",
            on_delete=models.CASCADE)
    position = models.IntegerField(default=1)

    class Meta:
        ordering = ('position', )


class NoteSource(models.Model):
    note = models.ForeignKey(
            'Note',
            verbose_name="Text",
            on_delete=models.CASCADE)
    source = models.ForeignKey(
            Source,
            verbose_name="Quelle",
            on_delete=models.CASCADE)
    comment = models.CharField(
            max_length=500,
            blank=True,
            verbose_name="Kommentar")


class Note(models.Model):

    title = models.CharField(max_length=200, verbose_name='Titel')
    link = models.CharField(
        max_length=50,
        unique=True,
        help_text='Link, unter dem der Text aufgerufen werden kann '
        '(ohne die Domain), zum Beispiel "/personen/mueller/otto/". '
        'Beginn und Ende "/", weitere "/" möglich; sonst nur a-z0-9. '
        'Keine Umlaute, Sonderzeichen, Leerzeichen, Satzzeichen außer ".".',
    )
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
        # pylint: disable=no-member
        super(Note, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.link:
            return '/n' + self.link
        else:
            return reverse('note-detail', kwargs={'pk': self.id, })

    def related_label(self):
        if Site.objects.get_current() in self.sites.all():
            return self.__str__()
        else:
            return '[[ %s ]]' % self.__str__()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title', )
        verbose_name = 'Text'
        verbose_name_plural = 'Texte'
