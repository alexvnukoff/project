# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'User.member'
        db.delete_column('appl_user', 'member_id')


    def backwards(self, orm):
        # Adding field 'User.member'
        db.add_column('appl_user', 'member',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='worker', default=0, to=orm['core.Item']),
                      keep_default=False)


    models = {
        'appl.advertising': {
            'Meta': {'object_name': 'Advertising', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.announce': {
            'Meta': {'object_name': 'Announce', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.article': {
            'Meta': {'object_name': 'Article', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.basket': {
            'Meta': {'object_name': 'Basket', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.cabinet': {
            'Meta': {'object_name': 'Cabinet', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.company': {
            'Meta': {'object_name': 'Company', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.department': {
            'Meta': {'object_name': 'Department', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'appl.document': {
            'Meta': {'object_name': 'Document', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.forum': {
            'Meta': {'object_name': 'Forum', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.forumpost': {
            'Meta': {'object_name': 'ForumPost', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.forumthread': {
            'Meta': {'object_name': 'ForumThread', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.invoice': {
            'Meta': {'object_name': 'Invoice', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.license': {
            'Meta': {'object_name': 'License', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.news': {
            'Meta': {'object_name': 'News', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.order': {
            'Meta': {'object_name': 'Order', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.payment': {
            'Meta': {'object_name': 'Payment', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.product': {
            'Meta': {'object_name': 'Product', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.rate': {
            'Meta': {'object_name': 'Rate', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.rating': {
            'Meta': {'object_name': 'Rating', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.review': {
            'Meta': {'object_name': 'Review', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.service': {
            'Meta': {'object_name': 'Service', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.shipment': {
            'Meta': {'object_name': 'Shipment', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.site': {
            'Meta': {'object_name': 'Site', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.tender': {
            'Meta': {'object_name': 'Tender', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.tpp': {
            'Meta': {'object_name': 'TPP', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Item']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'appl.user': {
            'Meta': {'object_name': 'User', '_ormbases': ['core.Identity']},
            'identity_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['core.Identity']", 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'created_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dict': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Dictionary']", 'related_name': "'attr'"}),
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
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'i2i'", 'to': "orm['core.Identity']", 'through': "orm['core.Participant']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.item': {
            'Meta': {'object_name': 'Item'},
            'attr': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'item'", 'to': "orm['core.Attribute']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['core.Item']", 'through': "orm['core.Relationship']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['core.State']"}),
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
            'Meta': {'object_name': 'Permission', 'unique_together': "(('title', 'role'),)"},
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
            'Meta': {'object_name': 'Relationship', 'unique_together': "(('parent', 'child'),)"},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'related_name': "'c2p'"}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'create_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Identity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Item']", 'related_name': "'p2c'"}),
            'qty': ('django.db.models.fields.FloatField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        },
        'core.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Permission']", 'related_name': "'state'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'})
        }
    }

    complete_apps = ['appl']