# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Participant'
        db.create_table('core_participant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
            ('community', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Identity'], related_name='comm2part')),
            ('part', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Identity'], related_name='part2comm')),
            ('date_from', self.gf('django.db.models.fields.DateField')(default=0)),
            ('date_to', self.gf('django.db.models.fields.DateField')(default=0)),
        ))
        db.send_create_signal('core', ['Participant'])


    def backwards(self, orm):
        # Deleting model 'Participant'
        db.delete_table('core_participant')


    models = {
        'core.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'created_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dict': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dictionary']", 'related_name': "'attr'"}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'updated_date': ('django.db.models.fields.DateField', [], {'blank': 'True', 'auto_now': 'True'})
        },
        'core.dictionary': {
            'Meta': {'object_name': 'Dictionary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.identity': {
            'Meta': {'object_name': 'Identity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Identity']", 'through': "orm['core.Participant']", 'related_name': "'i2i'", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.item': {
            'Meta': {'object_name': 'Item'},
            'attr': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Attribute']", 'related_name': "'item'", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Item']", 'through': "orm['core.Relationship']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.participant': {
            'Meta': {'object_name': 'Participant'},
            'community': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Identity']", 'related_name': "'comm2part'"}),
            'date_from': ('django.db.models.fields.DateField', [], {'default': '0'}),
            'date_to': ('django.db.models.fields.DateField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Identity']", 'related_name': "'part2comm'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.permission': {
            'Meta': {'unique_together': "(('title', 'role'),)", 'object_name': 'Permission'},
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
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.slot': {
            'Meta': {'object_name': 'Slot'},
            'dict': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dictionary']", 'related_name': "'slot'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Permission']", 'related_name': "'state'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.value': {
            'Meta': {'object_name': 'Value'},
            'attr': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Attribute']", 'related_name': "'value'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['core']