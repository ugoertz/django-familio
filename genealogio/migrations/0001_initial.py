# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import partialdate.fields
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('handle', models.CharField(unique=True, max_length=50)),
                ('private', models.BooleanField(default=False, verbose_name='private')),
                ('public', models.BooleanField(default=False, verbose_name='public')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_changed', models.DateTimeField(auto_now=True)),
                ('event_type', models.IntegerField(verbose_name='Typ', choices=[(1000, 'Unbekanntes Ereignis'), (990, 'Anderes Ereignis'), (80, 'Standesamtliche Hochzeit'), (90, 'Kirchliche Hochzeit'), (70, 'Verlobung'), (110, 'Scheidung'), (100, 'Verpartnerung'), (30, 'Adoption'), (20, 'Geburt'), (40, 'Tod'), (60, 'Taufe'), (150, 'Bestattung'), (160, 'Todesursache'), (120, 'Ausbildung'), (130, 'Beruf'), (140, 'Sport'), (50, 'Religion')])),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('date', partialdate.fields.PartialDateField(null=True, verbose_name='Datum', blank=True)),
                ('description', models.TextField(verbose_name='Beschreibung', blank=True)),
            ],
            options={
                'ordering': ('event_type',),
                'verbose_name': 'Ereignis',
                'verbose_name_plural': 'Ereignisse',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('handle', models.CharField(unique=True, max_length=50)),
                ('private', models.BooleanField(default=False, verbose_name='private')),
                ('public', models.BooleanField(default=False, verbose_name='public')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_changed', models.DateTimeField(auto_now=True)),
                ('family_rel_type', models.IntegerField(default=3, verbose_name='FamilyRelType', choices=[(0, 'Unbekannt'), (1, 'Andere'), (2, 'Verheiratet'), (3, 'Unverheiratet'), (4, 'Eingetragene Partnerschaft')])),
                ('start_date', partialdate.fields.PartialDateField(null=True, blank=True)),
                ('end_date', partialdate.fields.PartialDateField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Familie',
                'verbose_name_plural': 'Familien',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FamilyEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.IntegerField(default=-1, verbose_name='Rolle', choices=[(0, 'unbekannt'), (1, 'andere'), (2, 'Hauptperson'), (7, 'Familienmitglied')])),
                ('position', models.PositiveIntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Ereignis zu Familie',
                'verbose_name_plural': 'Ereignisse zu Familie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('typ', models.IntegerField(choices=[(-1, 'unbekannt'), (0, 'andere'), (1, 'Geburtsname'), (2, 'Ehename'), (3, 'Angenommener Name'), (4, 'Vorname'), (5, 'Rufname'), (6, 'Spitzname'), (7, 'Pseudonym'), (8, 'Familienname')])),
                ('position', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'Name',
                'verbose_name_plural': 'Namen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('handle', models.CharField(unique=True, max_length=50)),
                ('private', models.BooleanField(default=False, verbose_name='private')),
                ('public', models.BooleanField(default=False, verbose_name='public')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_changed', models.DateTimeField(auto_now=True)),
                ('last_name', models.CharField(default='', max_length=200, blank=True)),
                ('first_name', models.CharField(default='', max_length=200, blank=True)),
                ('gender_type', models.IntegerField(default=3, verbose_name='Geschlecht', choices=[(3, 'unbekannt'), (2, 'anderes'), (1, 'm\xe4nnlich'), (0, 'weiblich')])),
                ('probably_alive', models.BooleanField(default=False, verbose_name='Lebt wahrscheinlich noch')),
                ('comments', models.TextField(verbose_name='Kommentar', blank=True)),
                ('datebirth', partialdate.fields.PartialDateField(null=True, verbose_name='Geburtsdatum', blank=True)),
                ('datedeath', partialdate.fields.PartialDateField(null=True, verbose_name='Todesdatum', blank=True)),
            ],
            options={
                'ordering': ('handle', 'datebirth'),
                'verbose_name': 'Person',
                'verbose_name_plural': 'Personen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.IntegerField(default=-1, verbose_name='Rolle', choices=[(-1, 'unbekannt'), (1, 'andere'), (2, 'Hauptperson'), (3, 'Pate/Patin'), (4, 'Braut'), (5, 'Br\xe4utigam'), (6, 'Trauzeuge'), (7, 'Familienmitglied')])),
            ],
            options={
                'ordering': ('role',),
                'verbose_name': 'Ereignis zu Person',
                'verbose_name_plural': 'Ereignisse zu Person',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child_type', models.IntegerField(default=2, verbose_name='Typ', choices=[(0, 'unbekannt'), (1, 'anderer'), (2, 'Geburt'), (3, 'Adoption'), (4, 'Stiefkind'), (5, 'Pflegekind')])),
                ('position', models.PositiveIntegerField(default=1)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'Person-Familie-Beziehung',
                'verbose_name_plural': 'Person-Familie-Beziehungen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonPlace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', partialdate.fields.PartialDateField(null=True, blank=True)),
                ('end', partialdate.fields.PartialDateField(null=True, blank=True)),
                ('typ', models.IntegerField(choices=[(0, 'Unbekannt'), (1, 'Anderer'), (2, 'Geburt'), (3, 'Tod'), (4, 'Kindheit'), (5, 'Ausbildung/Studium'), (6, 'Ruhestand'), (7, 'Grabst\xe4tte')])),
                ('comment', models.CharField(default='', max_length=500, blank=True)),
            ],
            options={
                'ordering': ['start'],
                'verbose_name': 'Zugeordneter Ort',
                'verbose_name_plural': 'Zugeordnete Orte',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('handle', models.CharField(unique=True, max_length=50)),
                ('private', models.BooleanField(default=False, verbose_name='private')),
                ('public', models.BooleanField(default=False, verbose_name='public')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_changed', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('slug', models.SlugField(blank=True)),
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
            name='PlaceUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveIntegerField(default=1)),
                ('place', models.ForeignKey(to='genealogio.Place', on_delete=models.CASCADE)),
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
            field=models.ForeignKey(to='genealogio.Url', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
