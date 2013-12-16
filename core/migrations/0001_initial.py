# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Identity'
        db.create_table('core_identity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
        ))
        db.send_create_signal('core', ['Identity'])

        # Adding model 'Permission'
        db.create_table('core_permission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Identity'], related_name='identity')),
            ('create_flag', self.gf('django.db.models.fields.BooleanField')()),
            ('read_flag', self.gf('django.db.models.fields.BooleanField')()),
            ('update_flag', self.gf('django.db.models.fields.BooleanField')()),
            ('delete_flag', self.gf('django.db.models.fields.BooleanField')()),
            ('get_flag', self.gf('django.db.models.fields.BooleanField')()),
            ('run_flag', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal('core', ['Permission'])

        # Adding model 'State'
        db.create_table('core_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
        ))
        db.send_create_signal('core', ['State'])

        # Adding model 'Item'
        db.create_table('core_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.State'], null=True)),
        ))
        db.send_create_signal('core', ['Item'])

        # Adding model 'Relationship'
        db.create_table('core_relationship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Item'], related_name='p2c')),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Item'], related_name='c2p')),
            ('qty', self.gf('django.db.models.fields.FloatField')()),
            ('create_date', self.gf('django.db.models.fields.DateField')(blank=True, auto_now_add=True)),
            ('create_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Identity'])),
        ))
        db.send_create_signal('core', ['Relationship'])

        # Adding unique constraint on 'Relationship', fields ['parent', 'child']
        db.create_unique('core_relationship', ['parent_id', 'child_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Relationship', fields ['parent', 'child']
        db.delete_unique('core_relationship', ['parent_id', 'child_id'])

        # Deleting model 'Identity'
        db.delete_table('core_identity')

        # Deleting model 'Permission'
        db.delete_table('core_permission')

        # Deleting model 'State'
        db.delete_table('core_state')

        # Deleting model 'Item'
        db.delete_table('core_item')

        # Deleting model 'Relationship'
        db.delete_table('core_relationship')


    models = {
        'core.identity': {
            'Meta': {'object_name': 'Identity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.item': {
            'Meta': {'object_name': 'Item'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Item']", 'symmetrical': 'False', 'through': "orm['core.Relationship']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.permission': {
            'Meta': {'object_name': 'Permission'},
            'create_flag': ('django.db.models.fields.BooleanField', [], {}),
            'delete_flag': ('django.db.models.fields.BooleanField', [], {}),
            'get_flag': ('django.db.models.fields.BooleanField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read_flag': ('django.db.models.fields.BooleanField', [], {}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Identity']", 'related_name': "'identity'"}),
            'run_flag': ('django.db.models.fields.BooleanField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'}),
            'update_flag': ('django.db.models.fields.BooleanField', [], {})
        },
        'core.relationship': {
            'Meta': {'object_name': 'Relationship', 'unique_together': "(('parent', 'child'),)"},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'related_name': "'c2p'"}),
            'create_date': ('django.db.models.fields.DateField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'create_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Identity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'related_name': "'p2c'"}),
            'qty': ('django.db.models.fields.FloatField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        }
    }

    complete_apps = ['core']