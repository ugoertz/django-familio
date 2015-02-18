# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('doc', filebrowser.fields.FileBrowseField(max_length=200, null=True, verbose_name='Document', blank=True)),
                ('description', models.TextField(blank=True)),
                ('date', models.DateField(null=True, blank=True)),
                ('sites', models.ManyToManyField(to='sites.Site')),
            ],
            options={
                'ordering': ('date',),
                'verbose_name': 'Dokument',
                'verbose_name_plural': 'Dokumente',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('link', models.CharField(unique=True, max_length=50)),
                ('text', models.TextField()),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_changed', models.DateTimeField(auto_now=True)),
                ('published', models.BooleanField(default=True, verbose_name='Ver\xf6ffentlicht?')),
                ('authors', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Autoren', blank=True)),
            ],
            options={
                'ordering': ('link',),
                'verbose_name': 'Text',
                'verbose_name_plural': 'Texte',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', filebrowser.fields.FileBrowseField(max_length=200, null=True, verbose_name='Bilddatei', blank=True)),
                ('caption', models.TextField(verbose_name='Beschreibung', blank=True)),
                ('date', models.DateField(null=True, verbose_name='Datum', blank=True)),
                ('sites', models.ManyToManyField(to='sites.Site')),
            ],
            options={
                'verbose_name': 'Bild',
                'verbose_name_plural': 'Bilder',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('decription', models.TextField()),
                ('confidence_level', models.IntegerField(default=0, choices=[(0, 'unbekannt'), (1, 'zweifelhaft'), (2, 'unsicher'), (3, 'sicher'), (4, 'sehr sicher')])),
                ('media_type', models.IntegerField(default=0, choices=[(0, 'Unknown'), (5, 'Custom'), (6, 'Audio'), (7, 'Book'), (8, 'Card'), (9, 'Electronic'), (10, 'Fiche'), (11, 'Film'), (12, 'Magazine'), (13, 'Manuscript'), (14, 'Map'), (15, 'Newspaper'), (16, 'Photo'), (17, 'Tombstone'), (18, 'Video')])),
                ('documents', models.ManyToManyField(to='notaro.Document')),
                ('sites', models.ManyToManyField(to='sites.Site')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Quelle',
                'verbose_name_plural': 'Quellen',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='note',
            name='pictures',
            field=models.ManyToManyField(to='notaro.Picture', verbose_name='Bilder', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='note',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='note',
            name='source',
            field=models.ManyToManyField(to='notaro.Source', blank=True),
            preserve_default=True,
        ),
    ]
