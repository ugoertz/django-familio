# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0022_auto_20160228_1652'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventsource',
            old_name='person',
            new_name='event',
        ),
    ]
