# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '__first__'),
        ('notaro', '0009_auto_20150510_2033'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='tags',
            field=taggit.managers.TaggableManager(to='tags.CustomTag', through='tags.CustomTagThrough', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='picture',
            name='tags',
            field=taggit.managers.TaggableManager(to='tags.CustomTag', through='tags.CustomTagThrough', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
    ]
