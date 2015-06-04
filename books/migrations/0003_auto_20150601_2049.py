# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_item_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='use_custom_title_in_pdf',
            field=models.BooleanField(default=False, verbose_name='Eigenen Titel im PDF verwenden'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='obj_content_type',
            field=models.ForeignKey(verbose_name='Typ des zugeordneten Objekts', blank=True, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='obj_id',
            field=models.IntegerField(null=True, verbose_name='Zugeordnetes Objekt', blank=True),
            preserve_default=True,
        ),
    ]
