# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import partialdate.fields


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0004_auto_20150220_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='end_date',
            field=partialdate.fields.PartialDateField(null=True, verbose_name='Enddatum', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='family',
            name='father',
            field=models.ForeignKey(related_name='father_ref', verbose_name='Vater', blank=True, to='genealogio.Person', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='family',
            name='mother',
            field=models.ForeignKey(related_name='mother_ref', verbose_name='Mutter', blank=True, to='genealogio.Person', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='family',
            name='start_date',
            field=partialdate.fields.PartialDateField(null=True, verbose_name='Anfangsdatum', blank=True),
            preserve_default=True,
        ),
    ]
