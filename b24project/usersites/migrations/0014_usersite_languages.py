# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-10 21:43
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersites', '0013_auto_20161206_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersite',
            name='languages',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100, verbose_name='Languages'), blank=True, null=True, size=None),
        ),
    ]