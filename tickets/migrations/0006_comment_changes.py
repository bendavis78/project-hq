# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'TicketLogItem'
        db.delete_table('tickets_ticketlogitem')

        # Adding model 'TicketEvent'
        db.create_table('tickets_ticketevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['tickets.Ticket'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 2, 6, 17, 18, 18, 331664))),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('tickets', ['TicketEvent'])

        # Adding model 'TicketChange'
        db.create_table('tickets_ticketchange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='changes', to=orm['tickets.TicketEvent'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('tickets', ['TicketChange'])

        # Deleting field 'TicketComment.date'
        db.delete_column('tickets_ticketcomment', 'date')

        # Deleting field 'TicketComment.text'
        db.delete_column('tickets_ticketcomment', 'text')

        # Deleting field 'TicketComment.author'
        db.delete_column('tickets_ticketcomment', 'author_id')

        # Adding field 'TicketComment.event'
        db.add_column('tickets_ticketcomment', 'event', self.gf('django.db.models.fields.related.OneToOneField')(default=1, related_name='comment', unique=True, to=orm['tickets.TicketEvent']), keep_default=False)

        # Adding field 'TicketComment.message'
        db.add_column('tickets_ticketcomment', 'message', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'TicketLogItem'
        db.create_table('tickets_ticketlogitem', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('frozen_instance', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(related_name='history', to=orm['tickets.Ticket'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('tickets', ['TicketLogItem'])

        # Deleting model 'TicketEvent'
        db.delete_table('tickets_ticketevent')

        # Deleting model 'TicketChange'
        db.delete_table('tickets_ticketchange')

        # Adding field 'TicketComment.date'
        db.add_column('tickets_ticketcomment', 'date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 2, 6, 17, 18, 37, 723672)), keep_default=False)

        # Adding field 'TicketComment.text'
        db.add_column('tickets_ticketcomment', 'text', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'TicketComment.author'
        db.add_column('tickets_ticketcomment', 'author', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['auth.User']), keep_default=False)

        # Deleting field 'TicketComment.event'
        db.delete_column('tickets_ticketcomment', 'event_id')

        # Deleting field 'TicketComment.message'
        db.delete_column('tickets_ticketcomment', 'message')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 2, 6, 17, 19, 6, 470531)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 2, 6, 17, 19, 6, 470280)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'clients.client': {
            'Meta': {'ordering': "['name']", 'object_name': 'Client'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'clients.project': {
            'Meta': {'ordering': "['client', 'name']", 'object_name': 'Project'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'projects'", 'to': "orm['clients.Client']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'taskboard.task': {
            'Meta': {'ordering': "['-completed', 'priority']", 'object_name': 'Task'},
            'blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'completed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'effort': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clients.Project']"}),
            'tags': ('tagging.fields.TagField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"})
        },
        'taskboard.taskuser': {
            'Meta': {'object_name': 'TaskUser', 'db_table': "'auth_user'", '_ormbases': ['auth.User'], 'proxy': 'True'}
        },
        'tickets.ticket': {
            'Meta': {'ordering': "('priority', '-submitted_date')", 'object_name': 'Ticket'},
            'closed_reason': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_tickets'", 'null': 'True', 'to': "orm['auth.User']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clients.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '15'}),
            'submitted_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submitted_tickets'", 'to': "orm['auth.User']"}),
            'submitted_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 2, 6, 17, 19, 6, 478017)'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['taskboard.Task']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'tickets.ticketattachment': {
            'Meta': {'object_name': 'TicketAttachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['tickets.Ticket']"})
        },
        'tickets.ticketchange': {
            'Meta': {'object_name': 'TicketChange'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changes'", 'to': "orm['tickets.TicketEvent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'tickets.ticketcomment': {
            'Meta': {'object_name': 'TicketComment'},
            'event': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'comment'", 'unique': 'True', 'to': "orm['tickets.TicketEvent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        'tickets.ticketevent': {
            'Meta': {'object_name': 'TicketEvent'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 2, 6, 17, 19, 6, 471929)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': "orm['tickets.Ticket']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'tickets.ticketuser': {
            'Meta': {'object_name': 'TicketUser', 'db_table': "'auth_user'", '_ormbases': ['auth.User'], 'proxy': 'True'}
        }
    }

    complete_apps = ['tickets']
