# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0002_auto_20150523_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='custommap',
            name='map_style',
            field=models.CharField(max_length=50, null=True, verbose_name='Kartenstil', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custommapmarker',
            name='style',
            field=models.CharField(max_length=400, null=True, verbose_name='Stil', blank=True),
            preserve_default=True,
        ),
    ]
