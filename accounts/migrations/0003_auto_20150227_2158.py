# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0005_auto_20150223_2319'),
        ('accounts', '0002_auto_20150215_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='codemirror_keymap',
            field=models.IntegerField(default=0, choices=[(0, b'default'), (1, b'vim'), (2, b'sublime')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_on_comment_answer',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_on_message',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='person',
            field=models.ForeignKey(blank=True, to='genealogio.Person', null=True),
            preserve_default=True,
        ),
    ]
