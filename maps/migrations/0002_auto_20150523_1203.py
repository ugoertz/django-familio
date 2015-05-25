# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('maps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='Titel', blank=True)),
                ('description', models.TextField(verbose_name='Beschreibung', blank=True)),
                ('bbox', django.contrib.gis.db.models.fields.PolygonField(srid=4326, verbose_name='Begrenzung')),
                ('rendered', filebrowser.fields.FileBrowseField(help_text='Gerenderte Karte im png-Format', max_length=200, null=True, verbose_name='Bilddatei', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomMapMarker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=30, blank=True)),
                ('description', models.CharField(max_length=200, verbose_name='Beschreibung', blank='True')),
                ('label_offset_x', models.FloatField(default=0, verbose_name='Positionskorrektur Label X')),
                ('label_offset_y', models.FloatField(default=0, verbose_name='Positionskorrektur Label Y')),
                ('position', models.IntegerField(default=1)),
                ('custommap', models.ForeignKey(verbose_name='Karte', to='maps.CustomMap')),
                ('place', models.ForeignKey(verbose_name='Ort', to='maps.Place')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='custommap',
            name='markers',
            field=models.ManyToManyField(to='maps.Place', verbose_name='Markierungen', through='maps.CustomMapMarker', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custommap',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
            preserve_default=True,
        ),
    ]
