# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='sites',
            field=models.ManyToManyField(to='sites.Site', through='accounts.UserSite', blank=True),
            preserve_default=True,
        ),
    ]
