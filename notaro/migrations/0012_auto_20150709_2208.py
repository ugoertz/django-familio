# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0011_auto_20150621_2046'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ('title',), 'verbose_name': 'Text', 'verbose_name_plural': 'Texte'},
        ),
    ]
