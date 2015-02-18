# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('notaro', '0001_initial'),
        ('genealogio', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='place',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='place',
            name='urls',
            field=models.ManyToManyField(to='genealogio.Url', through='genealogio.PlaceUrl', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personplace',
            name='person',
            field=models.ForeignKey(to='genealogio.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personplace',
            name='place',
            field=models.ForeignKey(to='genealogio.Place'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personfamily',
            name='family',
            field=models.ForeignKey(verbose_name='Familie', to='genealogio.Family'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personfamily',
            name='person',
            field=models.ForeignKey(to='genealogio.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personevent',
            name='event',
            field=models.ForeignKey(verbose_name='Ereignis', to='genealogio.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personevent',
            name='person',
            field=models.ForeignKey(to='genealogio.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='events',
            field=models.ManyToManyField(to='genealogio.Event', verbose_name='Ereignisse', through='genealogio.PersonEvent', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='family',
            field=models.ManyToManyField(to='genealogio.Family', verbose_name='Familie(n)', through='genealogio.PersonFamily'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='places',
            field=models.ManyToManyField(to='genealogio.Place', verbose_name='Orte', through='genealogio.PersonPlace', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='portrait',
            field=models.ForeignKey(verbose_name='Portrait', blank=True, to='notaro.Picture', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='source',
            field=models.ManyToManyField(to='notaro.Source', verbose_name='Quelle', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='name',
            name='person',
            field=models.ForeignKey(to='genealogio.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='familyevent',
            name='event',
            field=models.ForeignKey(verbose_name='Ereignis', to='genealogio.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='familyevent',
            name='family',
            field=models.ForeignKey(verbose_name='Familie', to='genealogio.Family'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='family',
            name='events',
            field=models.ManyToManyField(to='genealogio.Event', through='genealogio.FamilyEvent', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='family',
            name='father',
            field=models.ForeignKey(related_name='father_ref', blank=True, to='genealogio.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='family',
            name='mother',
            field=models.ForeignKey(related_name='mother_ref', blank=True, to='genealogio.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='family',
            name='name',
            field=models.ManyToManyField(to='genealogio.Name', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='family',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='family',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='family',
            name='source',
            field=models.ManyToManyField(to='notaro.Source', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='notes',
            field=models.ManyToManyField(to='notaro.Note', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='place',
            field=models.ForeignKey(verbose_name='Ort', blank=True, to='genealogio.Place', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='source',
            field=models.ManyToManyField(to='notaro.Source', verbose_name='Quelle', blank=True),
            preserve_default=True,
        ),
    ]
