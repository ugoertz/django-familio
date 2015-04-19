# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import partialdate.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('genealogio', '0008_auto_20150312_2054'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimelineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('url', models.CharField(max_length=200, verbose_name='URL')),
                ('start_date', partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', verbose_name='Startdatum')),
                ('end_date', partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich); kann freibleiben', verbose_name='Enddatum')),
                ('description', models.TextField(null=True, verbose_name='Beschreibung', blank=True)),
                ('typ', models.IntegerField(verbose_name='Art des Ereignisses', choices=[(1, 'Anderes Ereignis'), (2, 'Krieg'), (3, 'Erfindung'), (5, 'Wirtschaftliches Ereignis'), (6, 'Krisenzeit'), (7, 'Umsturz, Revolution'), (8, 'Anderes Ereignis (blau)'), (9, 'Anderes Ereignis (gr\xfcn)'), (10, 'Anderes Ereignis (grau)')])),
                ('families', models.ManyToManyField(help_text='Sind hier Familien ausgew\xe4hlt, so wird der Eintrag nurbei den ausgew\xe4hlten Familien angezeigt, sonst bei allenFamilien', to='genealogio.Family', verbose_name='Familien', blank=True)),
                ('sites', models.ManyToManyField(to='sites.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
