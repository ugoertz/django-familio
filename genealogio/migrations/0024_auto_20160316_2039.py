# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import partialdate.fields


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0023_auto_20160303_2105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=partialdate.fields.PartialDateField(default='', help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', verbose_name='Datum', blank=True),
        ),
        migrations.AlterField(
            model_name='family',
            name='end_date',
            field=partialdate.fields.PartialDateField(default='', help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', verbose_name='Enddatum', blank=True),
        ),
        migrations.AlterField(
            model_name='family',
            name='start_date',
            field=partialdate.fields.PartialDateField(default='', help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', verbose_name='Anfangsdatum', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='datebirth',
            field=partialdate.fields.PartialDateField(default='', help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', verbose_name='Geburtsdatum', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='datedeath',
            field=partialdate.fields.PartialDateField(default='', help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', verbose_name='Todesdatum', blank=True),
        ),
        migrations.AlterField(
            model_name='personplace',
            name='end',
            field=partialdate.fields.PartialDateField(default='', help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', verbose_name='Ende', blank=True),
        ),
        migrations.AlterField(
            model_name='personplace',
            name='start',
            field=partialdate.fields.PartialDateField(default='', help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', verbose_name='Beginn', blank=True),
        ),
        migrations.AlterField(
            model_name='timelineitem',
            name='description',
            field=models.TextField(default='', help_text='Wird beim pdf-Export verwendet, kann als ReST formattiert werden, mit Links auf Objekte der Datenbank (siehe Dokumentation).', verbose_name='Beschreibung', blank=True),
        ),
        migrations.AlterField(
            model_name='timelineitem',
            name='end_date',
            field=partialdate.fields.PartialDateField(default='', help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich); kann freibleiben', verbose_name='Enddatum', blank=True),
        ),
        migrations.AlterField(
            model_name='timelineitem',
            name='start_date',
            field=partialdate.fields.PartialDateField(default='', help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', verbose_name='Startdatum', blank=True),
        ),
    ]
