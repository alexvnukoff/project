# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('b24online', '0005_auto_20160110_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='registeredevent',
            name='is_unique',
            field=models.BooleanField(default=False),
        ),
    ]
