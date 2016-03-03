# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0015_auto_20160302_2017'),
    ]

    operations = [
        migrations.RenameField(
            model_name='videosource',
            old_name='picture',
            new_name='video',
        ),
    ]
