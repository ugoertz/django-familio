# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0021_family_comments'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='family',
            options={'ordering': ('name', 'start_date', 'id'), 'verbose_name': 'Familie', 'verbose_name_plural': 'Familien'},
        ),
    ]
