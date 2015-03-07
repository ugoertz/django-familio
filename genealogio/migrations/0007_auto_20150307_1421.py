# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0001_initial'),
        ('genealogio', '0006_auto_20150307_1418'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=1)),
                ('event', models.ForeignKey(to='genealogio.Event')),
                ('note', models.ForeignKey(to='notaro.Note')),
            ],
            options={
                'verbose_name': 'Text zu Ereignis',
                'verbose_name_plural': 'Texte zu Ereignis',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FamilyNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=1)),
                ('family', models.ForeignKey(to='genealogio.Family')),
                ('note', models.ForeignKey(to='notaro.Note')),
            ],
            options={
                'verbose_name': 'Text zu Familie',
                'verbose_name_plural': 'Texte zu Familie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=1)),
                ('note', models.ForeignKey(to='notaro.Note')),
                ('person', models.ForeignKey(to='genealogio.Person')),
            ],
            options={
                'verbose_name': 'Text zu Person',
                'verbose_name_plural': 'Texte zu Person',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlaceNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=1)),
                ('note', models.ForeignKey(to='notaro.Note')),
                ('place', models.ForeignKey(to='genealogio.Place')),
            ],
            options={
                'verbose_name': 'Text zu Ort',
                'verbose_name_plural': 'Texte zu Ort',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', through='genealogio.EventNote', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='family',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', through='genealogio.FamilyNote', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', through='genealogio.PersonNote', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='place',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', through='genealogio.PlaceNote', blank=True),
            preserve_default=True,
        ),
    ]
