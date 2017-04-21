# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-20 11:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('b24online', '0030_auto_20170112_0944'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalParameters',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=1000)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterIndexTogether(
            name='additionalparameters',
            index_together=set([('content_type', 'object_id')]),
        ),
    ]
