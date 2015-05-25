# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0005_auto_20150525_1446'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='custommapmarker',
            options={'ordering': ('position',)},
        ),
    ]
