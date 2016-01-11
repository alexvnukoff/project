# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('b24online', '0004_auto_20160110_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registeredevent',
            name='url',
            field=models.TextField(null=True, verbose_name='Requested URL', blank=True),
        ),
        migrations.AlterField(
            model_name='registeredevent',
            name='user_agent',
            field=models.CharField(max_length=255, verbose_name='User Agent info', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='registeredevent',
            name='username',
            field=models.CharField(max_length=255, verbose_name='Username', blank=True, null=True),
        ),
    ]
