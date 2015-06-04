# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import books.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='Projekttitel', blank=True)),
                ('description', models.TextField(verbose_name='Kurzbeschreibung', blank=True)),
                ('public', models.BooleanField(default=False, verbose_name='Verf\xfcgbar f\xfcr andere Benutzer')),
                ('directory', models.CharField(max_length=300, blank=True)),
                ('render_status', models.CharField(max_length=800, verbose_name='Status', blank=True)),
                ('sphinx_conf', models.TextField(blank=True)),
                ('mogrify_options', models.CharField(max_length=300, blank=True)),
                ('flags', models.CharField(max_length=800, verbose_name='Einstellungen', blank=True)),
                ('titlepage', models.FileField(max_length=200, upload_to=books.models.get_upload_to, null=True, verbose_name='Titelseite', blank=True)),
                ('authors', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Autoren')),
            ],
            options={
                'verbose_name': 'Buch',
                'verbose_name_plural': 'B\xfccher',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='Titel', blank=True)),
                ('flags', models.CharField(max_length=800, verbose_name='Einstellungen', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='Aktiv')),
                ('level', models.IntegerField(default=0)),
                ('position', models.IntegerField(default=0)),
                ('order_by', models.CharField(help_text='Durch Kommata getrennte Datenbank-Felder, nach denen sortiert werden soll.', max_length=100, blank=True)),
                ('book', models.ForeignKey(verbose_name='Zugeh\xf6riges Buch', to='books.Book')),
                ('model', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('parent', models.ForeignKey(blank=True, to='books.Collection', null=True)),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'Kollektion',
                'verbose_name_plural': 'Kollektionen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('obj_id', models.IntegerField(null=True, blank=True)),
                ('text', models.TextField(verbose_name='Eigener Text', blank=True)),
                ('flags', models.CharField(max_length=800, verbose_name='Einstellungen', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='Aktiv')),
                ('position', models.IntegerField(default=1)),
                ('obj_content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('parent', models.ForeignKey(to='books.Collection')),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'Eintrag',
                'verbose_name_plural': 'Eintr\xe4ge',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='book',
            name='root',
            field=models.ForeignKey(related_name='book_root', blank=True, to='books.Collection', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='book',
            name='site',
            field=models.ForeignKey(verbose_name='Familienbaum', to='sites.Site'),
            preserve_default=True,
        ),
    ]
