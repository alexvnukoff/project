# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Permission', fields ['title']
        db.delete_unique('core_permission', ['title'])


    def backwards(self, orm):
        # Adding unique constraint on 'Permission', fields ['title']
        db.create_unique('core_permission', ['title'])


    models = {
        'core.identity': {
            'Meta': {'object_name': 'Identity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'core.item': {
            'Meta': {'object_name': 'Item'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'through': "orm['core.Relationship']", 'to': "orm['core.Item']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'core.permission': {
            'Meta': {'object_name': 'Permission'},
            'create_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'delete_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'get_flag': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read_flag': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Identity']", 'related_name': "'identity'"}),
            'run_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'update_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.relationship': {
            'Meta': {'unique_together': "(('parent', 'child'),)", 'object_name': 'Relationship'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'related_name': "'c2p'"}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'create_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Identity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'related_name': "'p2c'"}),
            'qty': ('django.db.models.fields.FloatField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'core.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Permission']", 'related_name': "'state'"}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        }
    }

    complete_apps = ['core']