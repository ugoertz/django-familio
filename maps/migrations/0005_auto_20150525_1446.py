# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0004_auto_20150525_1006'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='custommap',
            options={'ordering': ('-id',), 'verbose_name': 'Eigene Landkarte', 'verbose_name_plural': 'Eigene Landkarten'},
        ),
    ]
