# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Dictionary'
        db.create_table('core_dictionary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
        ))
        db.send_create_signal('core', ['Dictionary'])

        # Adding model 'Value'
        db.create_table('core_value', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('attr', self.gf('django.db.models.fields.related.ForeignKey')(related_name='value', to=orm['core.Attribute'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Item'])),
        ))
        db.send_create_signal('core', ['Value'])

        # Adding model 'Attribute'
        db.create_table('core_attribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('dict', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attr', to=orm['core.Dictionary'])),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('created_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('core', ['Attribute'])

        # Adding model 'Slot'
        db.create_table('core_slot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('dict', self.gf('django.db.models.fields.related.ForeignKey')(related_name='slot', to=orm['core.Dictionary'])),
        ))
        db.send_create_signal('core', ['Slot'])

        # Adding M2M table for field attr on 'Item'
        m2m_table_name = db.shorten_name('core_item_attr')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('item', models.ForeignKey(orm['core.item'], null=False)),
            ('attribute', models.ForeignKey(orm['core.attribute'], null=False))
        ))
        db.create_unique(m2m_table_name, ['item_id', 'attribute_id'])


    def backwards(self, orm):
        # Deleting model 'Dictionary'
        db.delete_table('core_dictionary')

        # Deleting model 'Value'
        db.delete_table('core_value')

        # Deleting model 'Attribute'
        db.delete_table('core_attribute')

        # Deleting model 'Slot'
        db.delete_table('core_slot')

        # Removing M2M table for field attr on 'Item'
        db.delete_table(db.shorten_name('core_item_attr'))


    models = {
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
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.item': {
            'Meta': {'object_name': 'Item'},
            'attr': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'item'", 'to': "orm['core.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'through': "orm['core.Relationship']", 'to': "orm['core.Item']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['core.State']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.permission': {
            'Meta': {'object_name': 'Permission', 'unique_together': "(('title', 'role'),)"},
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
        'core.relationship': {
            'Meta': {'object_name': 'Relationship', 'unique_together': "(('parent', 'child'),)"},
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