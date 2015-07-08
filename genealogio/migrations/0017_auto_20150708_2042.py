# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0016_auto_20150615_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='family_rel_type',
            field=models.IntegerField(default=3, verbose_name='Art der Beziehung', choices=[(0, 'Unbekannt'), (1, 'Andere'), (2, 'Verheiratet'), (3, 'Unverheiratet'), (4, 'Eingetragene Partnerschaft'), (5, 'Geschieden'), (6, 'Getrennt lebend')]),
            preserve_default=True,
        ),
    ]
