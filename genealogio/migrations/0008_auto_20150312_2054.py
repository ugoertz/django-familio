# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import partialdate.fields


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0007_auto_20150307_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', null=True, verbose_name='Datum', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='family',
            name='end_date',
            field=partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', null=True, verbose_name='Enddatum', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='family',
            name='start_date',
            field=partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', null=True, verbose_name='Anfangsdatum', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='datebirth',
            field=partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', null=True, verbose_name='Geburtsdatum', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='datedeath',
            field=partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', null=True, verbose_name='Todesdatum', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personplace',
            name='end',
            field=partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', null=True, verbose_name='Ende', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personplace',
            name='start',
            field=partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich)', null=True, verbose_name='Beginn', blank=True),
            preserve_default=True,
        ),
    ]
