# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import partialdate.fields


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0009_timelineitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timelineitem',
            options={'ordering': ('start_date', 'end_date', 'title'), 'verbose_name': 'Ereignis im Zeitstrahl', 'verbose_name_plural': 'Ereignisse im Zeitstrahl'},
        ),
        migrations.AlterField(
            model_name='timelineitem',
            name='description',
            field=models.TextField(help_text='Wird beim pdf-Export verwendet, kann als ReST formattiert werden, mit Links auf Objekte der Datenbank (siehe Dokumentation).', null=True, verbose_name='Beschreibung', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timelineitem',
            name='end_date',
            field=partialdate.fields.PartialDateField(help_text='Datum im Format JJJJ-MM-TT (Teilangaben m\xf6glich); kann freibleiben', null=True, verbose_name='Enddatum', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timelineitem',
            name='url',
            field=models.CharField(max_length=200, verbose_name='URL', blank=True),
            preserve_default=True,
        ),
    ]
