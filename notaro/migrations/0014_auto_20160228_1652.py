# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.manager
import filebrowser.fields
import django.contrib.sites.managers
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
        ('sites', '0001_initial'),
        ('notaro', '0013_auto_20160220_1634'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('video', filebrowser.fields.FileBrowseField(help_text='Videodatei, Formate: mp4, ogg, webm, vob.', max_length=200, null=True, verbose_name='Videodatei', blank=True)),
                ('poster', filebrowser.fields.FileBrowseField(help_text='Angezeigte Bilddatei (.jpg/.png)', max_length=200, null=True, verbose_name='Bilddatei', blank=True)),
                ('directory', models.CharField(max_length=300, blank=True)),
                ('caption', models.TextField(verbose_name='Beschreibung', blank=True)),
                ('date', models.DateField(null=True, verbose_name='Datum', blank=True)),
                ('sites', models.ManyToManyField(to='sites.Site')),
            ],
            options={
                'ordering': ('-id',),
                'verbose_name': 'Video',
                'verbose_name_plural': 'Videos',
            },
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='VideoSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=500, verbose_name='Kommentar', blank=True)),
                ('picture', models.ForeignKey(verbose_name='Video', to='notaro.Video', on_delete=models.CASCADE)),
                ('source', models.ForeignKey(verbose_name='Quelle', to='notaro.Source', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='video',
            name='sources',
            field=models.ManyToManyField(to='notaro.Source', verbose_name='Quellen', through='notaro.VideoSource', blank=True),
        ),
        migrations.AddField(
            model_name='video',
            name='tags',
            field=taggit.managers.TaggableManager(to='tags.CustomTag', through='tags.CustomTagThrough', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
    ]
