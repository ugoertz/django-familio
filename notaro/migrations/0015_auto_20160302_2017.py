# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0014_auto_20160228_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='image',
            field=filebrowser.fields.FileBrowseField(help_text='Bilddatei im jpg- oder png-Format', max_length=200, null=True, verbose_name='Bilddatei', blank=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='doc',
            field=filebrowser.fields.FileBrowseField(help_text='.pdf, .doc(x), .odt, .rtf, .jpg, .png, .tif, .mp3/4', max_length=200, null=True, verbose_name='Document', blank=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='video',
            field=filebrowser.fields.FileBrowseField(help_text='Videodatei, Formate: mp4, ogv, webm, vob.', max_length=200, null=True, verbose_name='Videodatei', blank=True),
        ),
    ]
