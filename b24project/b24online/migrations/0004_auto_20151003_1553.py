# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.contrib.postgres.fields.ranges


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('b24online', '0003_remove_order_polymorphic_ctype'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvertisementPrice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('advertisement_type', models.CharField(choices=[('banner', 'Banners'), ('context', 'Context Advertisement')], max_length=10)),
                ('object_id', models.PositiveIntegerField()),
                ('dates', django.contrib.postgres.fields.ranges.DateTimeRangeField()),
                ('price', models.DecimalField(max_digits=15, decimal_places=3)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(related_name='advertisementprice_create_user', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(related_name='advertisementprice_update_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='advertisementprices',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='advertisementprices',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='advertisementprices',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='advertisementprices',
            name='updated_by',
        ),
        migrations.AlterField(
            model_name='advertisementorder',
            name='price_components',
            field=models.ManyToManyField(to='b24online.AdvertisementPrice'),
        ),
        migrations.DeleteModel(
            name='AdvertisementPrices',
        ),
        migrations.AlterUniqueTogether(
            name='advertisementprice',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
