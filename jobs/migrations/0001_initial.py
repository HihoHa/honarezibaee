# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lft', models.PositiveIntegerField(db_index=True)),
                ('rgt', models.PositiveIntegerField(db_index=True)),
                ('tree_id', models.PositiveIntegerField(db_index=True)),
                ('depth', models.PositiveIntegerField(db_index=True)),
                ('name', models.CharField(unique=True, max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'w', max_length=4, choices=[(b'w', b'Waiting'), (b'r', b'Rejected')])),
                ('modified', models.DateTimeField(auto_now=True)),
                ('message', models.CharField(max_length=1000, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1000, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('address', models.TextField(null=True, blank=True)),
                ('email_address', models.EmailField(max_length=75, null=True, blank=True)),
                ('location', geoposition.fields.GeopositionField(max_length=42, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lft', models.PositiveIntegerField(db_index=True)),
                ('rgt', models.PositiveIntegerField(db_index=True)),
                ('tree_id', models.PositiveIntegerField(db_index=True)),
                ('depth', models.PositiveIntegerField(db_index=True)),
                ('name', models.CharField(unique=True, max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='jobchange',
            name='content',
            field=models.ForeignKey(to='jobs.JobContent', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobchange',
            name='job',
            field=models.ForeignKey(null=True, to='jobs.Job', unique=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='category',
            field=models.ManyToManyField(to='jobs.JobCategory', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='content',
            field=models.ForeignKey(to='jobs.JobContent', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='job',
            name='tags',
            field=models.ManyToManyField(to='jobs.JobTag', null=True, blank=True),
            preserve_default=True,
        ),
    ]
