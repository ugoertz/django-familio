# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0016_auto_20160303_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='date_added',
            field=models.DateTimeField(default=datetime.date(2016, 1, 1), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='date_changed',
            field=models.DateTimeField(default=datetime.date(2016, 1, 1), auto_now=True),
            preserve_default=False,
        ),
    ]
