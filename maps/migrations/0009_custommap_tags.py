# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
        ('maps', '0008_auto_20150613_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='custommap',
            name='tags',
            field=taggit.managers.TaggableManager(to='tags.CustomTag', through='tags.CustomTagThrough', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
    ]
