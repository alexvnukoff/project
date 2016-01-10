# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sites', '0001_initial'),
        ('b24online', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegisteredEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('url', models.TextField(verbose_name='Requested URL', blank=True)),
                ('username', models.CharField(verbose_name='Username', max_length=255, blank=True)),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP address of request', null=True, blank=True)),
                ('user_agent', models.CharField(verbose_name='User Agent info', max_length=255)),
                ('geoip_data', django_pgjson.fields.JsonBField(default={}, verbose_name='Geo information', blank=True)),
                ('extra_data', django_pgjson.fields.JsonBField(default={}, verbose_name='Event extra information', blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Registered event',
                'verbose_name_plural': 'Registered events',
            },
        ),
        migrations.CreateModel(
            name='RegisteredEventType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
                ('slug', models.SlugField(verbose_name='Code', max_length=20)),
            ],
            options={
                'verbose_name': 'Registered events type',
                'verbose_name_plural': 'Registered events types',
            },
        ),
        migrations.AddField(
            model_name='registeredevent',
            name='event_type',
            field=models.ForeignKey(verbose_name='Event  type', to='b24online.RegisteredEventType'),
        ),
        migrations.AddField(
            model_name='registeredevent',
            name='site',
            field=models.ForeignKey(verbose_name='Site', to='sites.Site'),
        ),
    ]
