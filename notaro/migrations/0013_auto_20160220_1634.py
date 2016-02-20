# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.manager
import django.contrib.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0012_auto_20150709_2208'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='document',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='note',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='picture',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='source',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]
