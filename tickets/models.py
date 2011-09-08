from django.db import models
from django.contrib.auth.models import User
from orderable.models import OrderableModel
from tagging.fields import TagField
from clients.models import Project
from taskboard.models import Task
from tickets.exceptions import TaskExists
from datetime import datetime
import os

TICKET_STATUS_CHOICES = (
    ('NEW', 'New'),
    ('ASSIGNED', 'Assigned'),
    ('ACKNOWLEGED', 'Acknowleged'),
    ('TASK', 'Scheduled for work'),
    ('FEEDBACK', 'Awating Feedback'),
    ('CLOSED', 'Closed'),
    ('INVALID', 'Invalid'),
)

class TicketUser(User):
    class Meta:
        proxy = True

    def __unicode__(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        if self.first_name:
            return self.first_name
        return self.username

class Ticket(OrderableModel):
    priority = models.IntegerField(null=True, editable=False)
    project = models.ForeignKey(Project)
    title = models.CharField(max_length=250)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=TICKET_STATUS_CHOICES, default='NEW')
    owner = models.ForeignKey(TicketUser, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    submitted_date = models.DateTimeField(default=datetime.today, editable=False)
    task = models.ForeignKey(Task, null=True, blank=True, editable=False)
    tags = TagField()
    
    ordering_field = 'priority'

    class Meta:
        ordering = ('-submitted_date',)
    
    def convert_to_task(self):
        if self.task:
            raise TaskExists("A task already exists for this ticket")
    
    @models.permalink
    def get_absolute_url(self):
        return ('ticket-details', (self.pk,))

    def __str__(self):
        return self.summary

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='attachments')
    attachment = models.FileField(upload_to="attachments")
    
    def __unicode__(self):
        return os.path.basename(self.attachment.name)

class TicketComment(models.Model):
    date = models.DateTimeField()
    author = models.ForeignKey(User)
    text = models.TextField()

class TicketLogItem(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='history')
    user = models.ForeignKey(User)
    description = models.CharField(max_length=250)
    frozen_instance = models.TextField(blank=True)
