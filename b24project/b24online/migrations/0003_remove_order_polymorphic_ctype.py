# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('b24online', '0002_order_polymorphic_ctype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='polymorphic_ctype',
        ),
    ]
