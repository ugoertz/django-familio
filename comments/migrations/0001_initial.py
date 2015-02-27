# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import dbarray.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('path', dbarray.fields.IntegerArrayField(unique=True, editable=False, blank=True)),
                ('object_pk', models.TextField(verbose_name='object ID')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_comment', verbose_name='content type', to='contenttypes.ContentType')),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
