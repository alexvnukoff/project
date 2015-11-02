# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('b24online', '0004_auto_20151003_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bannerblock',
            name='description',
            field=models.CharField(default='', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bannerblock',
            name='description_am',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='bannerblock',
            name='description_ar',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='bannerblock',
            name='description_en',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='bannerblock',
            name='description_he',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='bannerblock',
            name='description_ru',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='bannerblock',
            name='description_uk',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='bannerblock',
            name='description_zh',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]
