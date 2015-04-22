# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0010_auto_20150418_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timelineitem',
            name='typ',
            field=models.IntegerField(verbose_name='Art des Ereignisses', choices=[(1, 'Anderes Ereignis'), (2, 'Krieg'), (3, 'Erfindung'), (4, 'Politisches Ereignis'), (5, 'Wirtschaftliches Ereignis'), (6, 'Krisenzeit'), (7, 'Umsturz, Revolution'), (8, 'Anderes Ereignis (blau)'), (9, 'Anderes Ereignis (gr\xfcn)'), (10, 'Anderes Ereignis (grau)')]),
            preserve_default=True,
        ),
    ]
