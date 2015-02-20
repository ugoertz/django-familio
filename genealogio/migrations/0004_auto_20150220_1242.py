# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0003_auto_20150220_0733'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='family',
            options={'ordering': ('name',), 'verbose_name': 'Familie', 'verbose_name_plural': 'Familien'},
        ),
    ]
