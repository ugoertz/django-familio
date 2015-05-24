# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0003_auto_20150524_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='custommap',
            name='refresh',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='custommap',
            name='render_status',
            field=models.CharField(default='NOTRENDERED', max_length=800),
            preserve_default=True,
        ),
    ]
