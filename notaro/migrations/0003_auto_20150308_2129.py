# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notaro', '0002_remove_note_pictures'),
    ]

    operations = [
        migrations.CreateModel(
            name='PictureNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=1)),
                ('note', models.ForeignKey(verbose_name='Text', to='notaro.Note')),
                ('picture', models.ForeignKey(verbose_name='Bild', to='notaro.Picture')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='note',
            name='pictures',
            field=models.ManyToManyField(to='notaro.Picture', verbose_name='Bilder', through='notaro.PictureNote', blank=True),
            preserve_default=True,
        ),
    ]
