# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('b24online', '0002_auto_20160110_1107'),
    ]

    operations = [
        migrations.RunSQL("""
            INSERT INTO b24online_registeredeventtype (name, slug) 
                VALUES ('View the product', 'view');
            INSERT INTO b24online_registeredeventtype (name, slug) 
                VALUES ('Click on product', 'click');
            """),
    ]
