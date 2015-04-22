# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0011_auto_20150419_1133'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='family',
            options={'ordering': ('name', 'start_date'), 'verbose_name': 'Familie', 'verbose_name_plural': 'Familien'},
        ),
        migrations.AlterField(
            model_name='name',
            name='typ',
            field=models.IntegerField(choices=[(-1, 'unbekannt'), (0, 'andere'), (1, 'Geburtsname'), (2, 'Ehename'), (3, 'Angenommener Name'), (4, 'Vorname'), (5, 'Rufname'), (6, 'Spitzname'), (7, 'Pseudonym'), (8, 'Familienname'), (9, 'Titel (vorangest.)'), (10, 'Titel (nachgest.)'), (11, 'genannt')]),
            preserve_default=True,
        ),
    ]
