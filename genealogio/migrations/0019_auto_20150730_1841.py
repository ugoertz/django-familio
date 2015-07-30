# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genealogio', '0018_person_last_name_current'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timelineitem',
            name='families',
            field=models.ManyToManyField(help_text='Sind hier Familien ausgew\xe4hlt, so wird der Eintrag nur bei den ausgew\xe4hlten Familien angezeigt, sonst bei allen Familien', to='genealogio.Family', verbose_name='Familien', blank=True),
            preserve_default=True,
        ),
    ]
