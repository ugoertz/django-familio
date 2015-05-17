# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0009_auto_20150510_2033'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('slug', models.SlugField(blank=True)),
                ('handle', models.CharField(unique=True, max_length=50)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Ort',
                'verbose_name_plural': 'Orte',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlaceNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=1)),
                ('note', models.ForeignKey(to='notaro.Note')),
                ('place', models.ForeignKey(to='maps.Place')),
            ],
            options={
                'verbose_name': 'Text zu Ort',
                'verbose_name_plural': 'Texte zu Ort',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlaceUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveIntegerField(default=1)),
                ('place', models.ForeignKey(to='maps.Place')),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'URL zum Ort',
                'verbose_name_plural': 'URLs zum Ort',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('link', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='placeurl',
            name='url',
            field=models.ForeignKey(to='maps.Url'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='place',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', through='maps.PlaceNote', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='place',
            name='urls',
            field=models.ManyToManyField(to='maps.Url', through='maps.PlaceUrl', blank=True),
            preserve_default=True,
        ),
    ]
