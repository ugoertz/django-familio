# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import partialdate.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0018_auto_20160310_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date',
            field=partialdate.fields.PartialDateField(default='', verbose_name='Datum', blank=True),
        ),
        migrations.AlterField(
            model_name='picture',
            name='date',
            field=partialdate.fields.PartialDateField(default='', verbose_name='Datum', blank=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='date',
            field=partialdate.fields.PartialDateField(default='', verbose_name='Datum', blank=True),
        ),
    ]
