# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-16 11:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('b24online', '0021_auto_20161002_1818'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='additionalpage',
            index_together=set([('content_type', 'object_id')]),
        ),
    ]