# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0005_auto_20150312_2054'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=500, verbose_name='Kommentar', blank=True)),
                ('note', models.ForeignKey(verbose_name='Text', to='notaro.Note')),
                ('source', models.ForeignKey(verbose_name='Quelle', to='notaro.Source')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PictureSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=500, verbose_name='Kommentar', blank=True)),
                ('picture', models.ForeignKey(verbose_name='Bild', to='notaro.Picture')),
                ('source', models.ForeignKey(verbose_name='Quelle', to='notaro.Source')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='note',
            name='source',
        ),
        migrations.RemoveField(
            model_name='source',
            name='decription',
        ),
        migrations.RemoveField(
            model_name='source',
            name='media_type',
        ),
        migrations.AddField(
            model_name='note',
            name='sources',
            field=models.ManyToManyField(to='notaro.Source', verbose_name='Quellen', through='notaro.NoteSource', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='picture',
            name='sources',
            field=models.ManyToManyField(to='notaro.Source', verbose_name='Quellen', through='notaro.PictureSource', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='source',
            name='description',
            field=models.TextField(verbose_name='Beschreibung', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='source',
            name='confidence_level',
            field=models.IntegerField(default=0, verbose_name='Zuverl\xe4ssigkeit', choices=[(0, 'unbekannt'), (1, 'zweifelhaft'), (2, 'unsicher'), (3, 'sicher'), (4, 'sehr sicher')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='source',
            name='documents',
            field=models.ManyToManyField(to='notaro.Document', verbose_name='Dokumente'),
            preserve_default=True,
        ),
    ]
