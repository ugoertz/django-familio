# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-28 14:20
from __future__ import unicode_literals

import django.contrib.sites.managers
from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0010_auto_20160220_1634'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='custommap',
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]
