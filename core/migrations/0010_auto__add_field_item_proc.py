# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Item.proc'
        db.add_column('core_item', 'proc',
                      self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Process']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Item.proc'
        db.delete_column('core_item', 'proc_id')


    models = {
        'core.action': {
            'Meta': {'object_name': 'Action'},
            'child_proc': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'start_node'", 'default': '0', 'to': "orm['core.Process']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'papa': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'action'", 'to': "orm['core.Process']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.actionpath': {
            'Meta': {'object_name': 'ActionPath'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'act2path'", 'to': "orm['core.Action']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'path2act'", 'to': "orm['core.Action']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'created_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dict': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attr'", 'to': "orm['core.Dictionary']"}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'updated_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.dictionary': {
            'Meta': {'object_name': 'Dictionary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.identity': {
            'Meta': {'object_name': 'Identity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'through': "orm['core.Participant']", 'related_name': "'i2i'", 'symmetrical': 'False', 'to': "orm['core.Identity']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.item': {
            'Meta': {'object_name': 'Item'},
            'attr': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'item'", 'symmetrical': 'False', 'to': "orm['core.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'through': "orm['core.Relationship']", 'symmetrical': 'False', 'to': "orm['core.Item']"}),
            'proc': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['core.Process']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['core.State']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.participant': {
            'Meta': {'object_name': 'Participant'},
            'community': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comm2part'", 'to': "orm['core.Identity']"}),
            'date_from': ('django.db.models.fields.DateField', [], {'default': '0'}),
            'date_to': ('django.db.models.fields.DateField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'part2comm'", 'to': "orm['core.Identity']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.permission': {
            'Meta': {'unique_together': "(('title', 'role'),)", 'object_name': 'Permission'},
            'create_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'delete_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'get_flag': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read_flag': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'identity'", 'to': "orm['core.Identity']"}),
            'run_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'update_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.process': {
            'Meta': {'object_name': 'Process'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.relationship': {
            'Meta': {'unique_together': "(('parent', 'child'),)", 'object_name': 'Relationship'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'c2p'", 'to': "orm['core.Item']"}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'create_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Identity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'p2c'", 'to': "orm['core.Item']"}),
            'qty': ('django.db.models.fields.FloatField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.slot': {
            'Meta': {'object_name': 'Slot'},
            'dict': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'slot'", 'to': "orm['core.Dictionary']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perm': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'state'", 'to': "orm['core.Permission']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.value': {
            'Meta': {'object_name': 'Value'},
            'attr': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'value'", 'to': "orm['core.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        }
    }

    complete_apps = ['core']