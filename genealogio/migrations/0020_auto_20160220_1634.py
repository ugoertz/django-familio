# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager
import django.contrib.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0019_auto_20150730_1841'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='event',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='family',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='person',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='timelineitem',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]
