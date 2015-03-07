# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0005_auto_20150223_2319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='family',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='person',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='place',
            name='notes',
        ),
        migrations.AlterField(
            model_name='family',
            name='family_rel_type',
            field=models.IntegerField(default=3, verbose_name='Art der Beziehung', choices=[(0, 'Unbekannt'), (1, 'Andere'), (2, 'Verheiratet'), (3, 'Unverheiratet'), (4, 'Eingetragene Partnerschaft')]),
            preserve_default=True,
        ),
    ]
