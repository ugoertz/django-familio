# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0008_document_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date',
            field=models.DateField(null=True, verbose_name='Datum', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='description',
            field=models.TextField(verbose_name='Beschreibung', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='document',
            name='name',
            field=models.CharField(max_length=500, verbose_name='Name'),
            preserve_default=True,
        ),
    ]
