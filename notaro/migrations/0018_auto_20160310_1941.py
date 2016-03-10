# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import partialdate.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0017_auto_20160305_0826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date',
            field=partialdate.fields.PartialDateField(null=True, verbose_name='Datum', blank=True),
        ),
        migrations.AlterField(
            model_name='picture',
            name='date',
            field=partialdate.fields.PartialDateField(null=True, verbose_name='Datum', blank=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='date',
            field=partialdate.fields.PartialDateField(null=True, verbose_name='Datum', blank=True),
        ),
    ]
