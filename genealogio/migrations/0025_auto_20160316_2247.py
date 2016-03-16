# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0024_auto_20160316_2039'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ('date', 'event_type'), 'verbose_name': 'Ereignis', 'verbose_name_plural': 'Ereignisse'},
        ),
    ]
