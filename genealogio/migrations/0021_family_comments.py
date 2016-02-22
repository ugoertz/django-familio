# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0020_auto_20160220_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='comments',
            field=models.TextField(verbose_name='Kommentar', blank=True),
        ),
    ]
