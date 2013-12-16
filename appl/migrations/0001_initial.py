# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TPP'
        db.create_table('appl_tpp', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['TPP'])

        # Adding model 'Company'
        db.create_table('appl_company', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Company'])

        # Adding model 'Department'
        db.create_table('appl_department', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('appl', ['Department'])

        # Adding model 'User'
        db.create_table('appl_user', (
            ('identity_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Identity'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='worker', to=orm['core.Item'])),
        ))
        db.send_create_signal('appl', ['User'])

        # Adding model 'Site'
        db.create_table('appl_site', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Site'])

        # Adding model 'Product'
        db.create_table('appl_product', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Product'])

        # Adding model 'License'
        db.create_table('appl_license', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['License'])

        # Adding model 'Service'
        db.create_table('appl_service', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Service'])

        # Adding model 'Invoice'
        db.create_table('appl_invoice', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Invoice'])

        # Adding model 'News'
        db.create_table('appl_news', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['News'])

        # Adding model 'Article'
        db.create_table('appl_article', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Article'])

        # Adding model 'Announce'
        db.create_table('appl_announce', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Announce'])

        # Adding model 'Review'
        db.create_table('appl_review', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Review'])

        # Adding model 'Rating'
        db.create_table('appl_rating', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Rating'])

        # Adding model 'Payment'
        db.create_table('appl_payment', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Payment'])

        # Adding model 'Shipment'
        db.create_table('appl_shipment', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Shipment'])

        # Adding model 'Tender'
        db.create_table('appl_tender', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Tender'])

        # Adding model 'Advertising'
        db.create_table('appl_advertising', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Advertising'])

        # Adding model 'Rate'
        db.create_table('appl_rate', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Rate'])

        # Adding model 'Forum'
        db.create_table('appl_forum', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Forum'])

        # Adding model 'ForumThread'
        db.create_table('appl_forumthread', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['ForumThread'])

        # Adding model 'ForumPost'
        db.create_table('appl_forumpost', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['ForumPost'])

        # Adding model 'Order'
        db.create_table('appl_order', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Order'])

        # Adding model 'Basket'
        db.create_table('appl_basket', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Basket'])

        # Adding model 'Cabinet'
        db.create_table('appl_cabinet', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Cabinet'])

        # Adding model 'Document'
        db.create_table('appl_document', (
            ('item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('appl', ['Document'])


    def backwards(self, orm):
        # Deleting model 'TPP'
        db.delete_table('appl_tpp')

        # Deleting model 'Company'
        db.delete_table('appl_company')

        # Deleting model 'Department'
        db.delete_table('appl_department')

        # Deleting model 'User'
        db.delete_table('appl_user')

        # Deleting model 'Site'
        db.delete_table('appl_site')

        # Deleting model 'Product'
        db.delete_table('appl_product')

        # Deleting model 'License'
        db.delete_table('appl_license')

        # Deleting model 'Service'
        db.delete_table('appl_service')

        # Deleting model 'Invoice'
        db.delete_table('appl_invoice')

        # Deleting model 'News'
        db.delete_table('appl_news')

        # Deleting model 'Article'
        db.delete_table('appl_article')

        # Deleting model 'Announce'
        db.delete_table('appl_announce')

        # Deleting model 'Review'
        db.delete_table('appl_review')

        # Deleting model 'Rating'
        db.delete_table('appl_rating')

        # Deleting model 'Payment'
        db.delete_table('appl_payment')

        # Deleting model 'Shipment'
        db.delete_table('appl_shipment')

        # Deleting model 'Tender'
        db.delete_table('appl_tender')

        # Deleting model 'Advertising'
        db.delete_table('appl_advertising')

        # Deleting model 'Rate'
        db.delete_table('appl_rate')

        # Deleting model 'Forum'
        db.delete_table('appl_forum')

        # Deleting model 'ForumThread'
        db.delete_table('appl_forumthread')

        # Deleting model 'ForumPost'
        db.delete_table('appl_forumpost')

        # Deleting model 'Order'
        db.delete_table('appl_order')

        # Deleting model 'Basket'
        db.delete_table('appl_basket')

        # Deleting model 'Cabinet'
        db.delete_table('appl_cabinet')

        # Deleting model 'Document'
        db.delete_table('appl_document')


    models = {
        'appl.advertising': {
            'Meta': {'object_name': 'Advertising', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.announce': {
            'Meta': {'object_name': 'Announce', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.article': {
            'Meta': {'object_name': 'Article', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.basket': {
            'Meta': {'object_name': 'Basket', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.cabinet': {
            'Meta': {'object_name': 'Cabinet', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.company': {
            'Meta': {'object_name': 'Company', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.department': {
            'Meta': {'object_name': 'Department', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'appl.document': {
            'Meta': {'object_name': 'Document', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.forum': {
            'Meta': {'object_name': 'Forum', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.forumpost': {
            'Meta': {'object_name': 'ForumPost', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.forumthread': {
            'Meta': {'object_name': 'ForumThread', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.invoice': {
            'Meta': {'object_name': 'Invoice', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.license': {
            'Meta': {'object_name': 'License', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.news': {
            'Meta': {'object_name': 'News', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.order': {
            'Meta': {'object_name': 'Order', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.payment': {
            'Meta': {'object_name': 'Payment', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.product': {
            'Meta': {'object_name': 'Product', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.rate': {
            'Meta': {'object_name': 'Rate', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.rating': {
            'Meta': {'object_name': 'Rating', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.review': {
            'Meta': {'object_name': 'Review', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.service': {
            'Meta': {'object_name': 'Service', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.shipment': {
            'Meta': {'object_name': 'Shipment', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.site': {
            'Meta': {'object_name': 'Site', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.tender': {
            'Meta': {'object_name': 'Tender', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.tpp': {
            'Meta': {'object_name': 'TPP', '_ormbases': ['core.Item']},
            'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Item']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'appl.user': {
            'Meta': {'object_name': 'User', '_ormbases': ['core.Identity']},
            'identity_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Identity']", 'unique': 'True', 'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worker'", 'to': "orm['core.Item']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'created_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dict': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attr'", 'to': "orm['core.Dictionary']"}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'updated_date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.dictionary': {
            'Meta': {'object_name': 'Dictionary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'core.identity': {
            'Meta': {'object_name': 'Identity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'core.item': {
            'Meta': {'object_name': 'Item'},
            'attr': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['core.Attribute']", 'related_name': "'item'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'through': "orm['core.Relationship']", 'to': "orm['core.Item']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.State']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
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
        'core.relationship': {
            'Meta': {'unique_together': "(('parent', 'child'),)", 'object_name': 'Relationship'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'c2p'", 'to': "orm['core.Item']"}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'create_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Identity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'p2c'", 'to': "orm['core.Item']"}),
            'qty': ('django.db.models.fields.FloatField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'core.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perm': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'state'", 'to': "orm['core.Permission']"}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        }
    }

    complete_apps = ['appl']