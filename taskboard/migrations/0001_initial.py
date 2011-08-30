# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Client'
        db.create_table('taskboard_client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('taskboard', ['Client'])

        # Adding model 'Project'
        db.create_table('taskboard_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['taskboard.Client'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('taskboard', ['Project'])

        # Adding model 'Task'
        db.create_table('taskboard_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['taskboard.Project'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('effort', self.gf('django.db.models.fields.IntegerField')()),
            ('completed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('blocked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('icebox', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('taskboard', ['Task'])


    def backwards(self, orm):
        
        # Deleting model 'Client'
        db.delete_table('taskboard_client')

        # Deleting model 'Project'
        db.delete_table('taskboard_project')

        # Deleting model 'Task'
        db.delete_table('taskboard_task')


    models = {
        'taskboard.client': {
            'Meta': {'ordering': "['name']", 'object_name': 'Client'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'taskboard.project': {
            'Meta': {'ordering': "['client', 'name']", 'object_name': 'Project'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['taskboard.Client']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'taskboard.task': {
            'Meta': {'ordering': "['-completed', 'priority']", 'object_name': 'Task'},
            'blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'completed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'effort': ('django.db.models.fields.IntegerField', [], {}),
            'icebox': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['taskboard.Project']"})
        }
    }

    complete_apps = ['taskboard']
