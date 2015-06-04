# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Titel', blank=True),
            preserve_default=True,
        ),
    ]
