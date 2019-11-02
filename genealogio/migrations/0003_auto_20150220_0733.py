# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import partialdate.fields


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0002_auto_20150216_0920'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='family',
            name='name',
        ),
        migrations.AddField(
            model_name='family',
            name='name',
            field=models.CharField(max_length=200, null=True, verbose_name='Familienname', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personplace',
            name='comment',
            field=models.CharField(default='', max_length=500, verbose_name='Kommentar', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personplace',
            name='end',
            field=partialdate.fields.PartialDateField(null=True, verbose_name='Ende', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personplace',
            name='place',
            field=models.ForeignKey(verbose_name='Ort', to='genealogio.Place', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personplace',
            name='start',
            field=partialdate.fields.PartialDateField(null=True, verbose_name='Beginn', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='personplace',
            name='typ',
            field=models.IntegerField(default=1, choices=[(0, 'Unbekannt'), (1, 'Anderer'), (2, 'Geburt'), (3, 'Tod'), (4, 'Kindheit'), (5, 'Ausbildung/Studium'), (6, 'Ruhestand'), (7, 'Grabst\xe4tte')]),
            preserve_default=True,
        ),
    ]
