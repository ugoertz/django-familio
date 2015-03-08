# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0003_auto_20150308_2129'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='picturenote',
            options={'ordering': ('position',)},
        ),
    ]
