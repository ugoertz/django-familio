# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0015_auto_20150614_2120'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventsource',
            options={'ordering': ('position',)},
        ),
        migrations.AlterModelOptions(
            name='familysource',
            options={'ordering': ('position',)},
        ),
        migrations.AlterModelOptions(
            name='personsource',
            options={'ordering': ('position',)},
        ),
        migrations.AddField(
            model_name='eventsource',
            name='position',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='familysource',
            name='position',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personsource',
            name='position',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
