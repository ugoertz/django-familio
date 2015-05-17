# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0013_auto_20150423_1419'),
        ('maps', '0001_initial')
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='place',
            name='sites',
        ),
        migrations.RemoveField(
            model_name='place',
            name='urls',
        ),
        migrations.RemoveField(
            model_name='placenote',
            name='note',
        ),
        migrations.RemoveField(
            model_name='placenote',
            name='place',
        ),
        migrations.DeleteModel(
            name='PlaceNote',
        ),
        migrations.RemoveField(
            model_name='placeurl',
            name='place',
        ),
        migrations.RemoveField(
            model_name='placeurl',
            name='url',
        ),
        migrations.DeleteModel(
            name='PlaceUrl',
        ),
        migrations.DeleteModel(
            name='Url',
        ),
        migrations.AlterField(
            model_name='event',
            name='place',
            field=models.ForeignKey(verbose_name='Ort', blank=True, to='maps.Place', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='places',
            field=models.ManyToManyField(to='maps.Place', verbose_name='Orte', through='genealogio.PersonPlace', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personplace',
            name='place',
            field=models.ForeignKey(verbose_name='Ort', to='maps.Place'),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='Place',
        ),
    ]
