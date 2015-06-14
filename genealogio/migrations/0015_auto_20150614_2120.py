# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0014_auto_20150517_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=models.CharField(default='', max_length=200, verbose_name='Vorname', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='last_name',
            field=models.CharField(default='', max_length=200, verbose_name='Geburtsname', blank=True),
            preserve_default=True,
        ),
    ]
