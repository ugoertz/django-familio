# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20150227_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='email_on_comment_answer',
            field=models.BooleanField(default=False, verbose_name=b'Email-Benachrichtigung bei Antwort auf meine Kommentare'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='email_on_message',
            field=models.BooleanField(default=False, verbose_name=b'Email-Benachrichtigung bei Nachrichten'),
            preserve_default=True,
        ),
    ]
