# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0006_auto_20150423_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='documents',
            field=models.ManyToManyField(to='notaro.Document', verbose_name='Dokumente', blank=True),
            preserve_default=True,
        ),
    ]
