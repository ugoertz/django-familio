# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0006_auto_20150423_1419'),
        ('genealogio', '0012_auto_20150422_1701'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=500, verbose_name='Kommentar', blank=True)),
                ('person', models.ForeignKey(verbose_name='Ereignis', to='genealogio.Event')),
                ('source', models.ForeignKey(verbose_name='Quelle', to='notaro.Source')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FamilySource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=500, verbose_name='Kommentar', blank=True)),
                ('family', models.ForeignKey(verbose_name='Familie', to='genealogio.Family')),
                ('source', models.ForeignKey(verbose_name='Quelle', to='notaro.Source')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(max_length=500, verbose_name='Kommentar', blank=True)),
                ('person', models.ForeignKey(verbose_name='Person', to='genealogio.Person')),
                ('source', models.ForeignKey(verbose_name='Quelle', to='notaro.Source')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='event',
            name='source',
        ),
        migrations.RemoveField(
            model_name='family',
            name='source',
        ),
        migrations.RemoveField(
            model_name='person',
            name='source',
        ),
        migrations.AddField(
            model_name='event',
            name='sources',
            field=models.ManyToManyField(to='notaro.Source', verbose_name='Quellen', through='genealogio.EventSource', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='family',
            name='sources',
            field=models.ManyToManyField(to='notaro.Source', verbose_name='Quellen', through='genealogio.FamilySource', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='sources',
            field=models.ManyToManyField(to='notaro.Source', verbose_name='Quellen', through='genealogio.PersonSource', blank=True),
            preserve_default=True,
        ),
    ]
