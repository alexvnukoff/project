# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-24 18:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('b24online', '0023_auto_20161016_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leadsstore',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='b24online.Organization'),
        ),
    ]
