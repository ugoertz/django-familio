# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.manager
import maps.managers


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0009_custommap_tags'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='custommap',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', maps.managers.CurrentSiteGeoManager()),
            ],
        ),
    ]
