# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_auto_20160220_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='path',
            field=django.contrib.postgres.fields.ArrayField(size=None, base_field=models.IntegerField(), unique=True, editable=False, blank=True),
        ),
    ]
