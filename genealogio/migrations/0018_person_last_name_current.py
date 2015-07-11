# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0017_auto_20150708_2042'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='last_name_current',
            field=models.CharField(default='', max_length=200, verbose_name='Aktueller Nachname', blank=True),
            preserve_default=True,
        ),
    ]
