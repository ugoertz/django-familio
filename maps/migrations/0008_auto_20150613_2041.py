# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0007_auto_20150531_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, verbose_name='Geo-Koordinaten', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='place',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', verbose_name='Texte', through='maps.PlaceNote', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='place',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Titel', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='place',
            name='urls',
            field=models.ManyToManyField(to='maps.Url', verbose_name='URLs', through='maps.PlaceUrl', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='placenote',
            name='note',
            field=models.ForeignKey(verbose_name='Text', to='notaro.Note'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='placenote',
            name='place',
            field=models.ForeignKey(verbose_name='Ort', to='maps.Place'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='placeurl',
            name='place',
            field=models.ForeignKey(verbose_name='Ort', to='maps.Place'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='placeurl',
            name='url',
            field=models.ForeignKey(verbose_name='URL', to='maps.Url'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='url',
            name='link',
            field=models.CharField(max_length=200, verbose_name='Link'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='url',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Titel', blank=True),
            preserve_default=True,
        ),
    ]
