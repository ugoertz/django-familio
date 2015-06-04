# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0006_auto_20150525_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custommap',
            name='refresh',
            field=models.BooleanField(default=False, verbose_name='Gerenderte Karte aktualisieren'),
            preserve_default=True,
        ),
    ]
