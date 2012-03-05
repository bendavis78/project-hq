# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'TicketEvent'
        db.delete_table('tickets_ticketevent')

        # Deleting model 'TicketChange'
        db.delete_table('tickets_ticketchange')

        # Deleting model 'TicketComment'
        db.delete_table('tickets_ticketcomment')

        # Deleting field 'Ticket.task'
        db.delete_column('tickets_ticket', 'task_id')


    def backwards(self, orm):
        
        # Adding model 'TicketEvent'
        db.create_table('tickets_ticketevent', (
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 2, 6, 17, 19, 6, 471929))),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['tickets.Ticket'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('tickets', ['TicketEvent'])

        # Adding model 'TicketChange'
        db.create_table('tickets_ticketchange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='changes', to=orm['tickets.TicketEvent'])),
        ))
        db.send_create_signal('tickets', ['TicketChange'])

        # Adding model 'TicketComment'
        db.create_table('tickets_ticketcomment', (
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('event', self.gf('django.db.models.fields.related.OneToOneField')(related_name='comment', unique=True, to=orm['tickets.TicketEvent'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('tickets', ['TicketComment'])

        # Adding field 'Ticket.task'
        db.add_column('tickets_ticket', 'task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['taskboard.Task'], null=True, blank=True), keep_default=False)


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 2, 12, 23, 35, 19, 835300)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 2, 12, 23, 35, 19, 835238)'}),
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
            'submitted_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 2, 12, 23, 35, 19, 835988)'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'tickets.ticketattachment': {
            'Meta': {'object_name': 'TicketAttachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['tickets.Ticket']"})
        },
        'tickets.ticketuser': {
            'Meta': {'object_name': 'TicketUser', 'db_table': "'auth_user'", '_ormbases': ['auth.User'], 'proxy': 'True'}
        }
    }

    complete_apps = ['tickets']
