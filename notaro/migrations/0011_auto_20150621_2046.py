# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0010_auto_20150618_2135'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='picture',
            options={'ordering': ('-id',), 'verbose_name': 'Bild', 'verbose_name_plural': 'Bilder'},
        ),
    ]
