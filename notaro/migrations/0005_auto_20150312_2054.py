# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0004_auto_20150308_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='doc',
            field=filebrowser.fields.FileBrowseField(help_text='.pdf, .doc, .rtf, .jpg, .tif, .mp3, .mp4', max_length=200, null=True, verbose_name='Document', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='picture',
            name='image',
            field=filebrowser.fields.FileBrowseField(help_text='Bilddatei im jpg- oder png-Format', max_length=200, null=True, verbose_name='Bilddatei', blank=True),
            preserve_default=True,
        ),
    ]
