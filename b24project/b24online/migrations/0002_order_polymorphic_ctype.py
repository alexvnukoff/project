# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('b24online', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='polymorphic_ctype',
            field=models.ForeignKey(to='contenttypes.ContentType', related_name='polymorphic_b24online.order_set+', null=True, editable=False),
        ),
    ]
