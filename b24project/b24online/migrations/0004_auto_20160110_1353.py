# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('b24online', '0003_auto_20160110_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registeredevent',
            name='site',
            field=models.ForeignKey(to='sites.Site', null=True, verbose_name='Site'),
        ),
    ]
