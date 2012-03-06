from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from tagging.fields import TagField
from clients.models import Project
from tickets.exceptions import TaskExists
from orderable.models import OrderableModel
from history.models import HistoryModel
from datetime import datetime
import os

TICKET_STATUS_CHOICES = (
    ('NEW', 'New'),
    ('ASSIGNED', 'Assigned'),
    ('ACKNOWLEGED', 'Acknowleged'),
    ('TASK', 'Scheduled for work'),
    ('FEEDBACK', 'Awating Feedback'),
    ('CLOSED', 'Closed'),
)

TICKET_CLOSED_REASONS = (
    ('RESOLVED', 'Resolved'),
    ('DUPLICATE', 'Duplicate'),
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

class Ticket(OrderableModel, HistoryModel, models.Model):
    submitted_by = models.ForeignKey(TicketUser, related_name='submitted_tickets')
    priority = models.IntegerField(null=True, editable=False, db_index=True)
    project = models.ForeignKey(Project)
    title = models.CharField(max_length=250)
    status = models.CharField(max_length=15, choices=TICKET_STATUS_CHOICES, default='NEW')
    closed_reason = models.CharField(max_length=15, choices=TICKET_CLOSED_REASONS, blank=True)
    owner = models.ForeignKey(TicketUser, null=True, blank=True, related_name='owned_tickets')
    due_date = models.DateField(null=True, blank=True)
    submitted_date = models.DateTimeField(default=datetime.today, editable=False)
    description = models.TextField()
    tags = TagField()

    ordering_field = 'priority'
    
    class Meta:
        ordering = ('priority','-submitted_date')
    
    @models.permalink
    def get_absolute_url(self):
        return ('ticket_details', (self.pk,))
   
    def save(self):
        if self.status == 'NEW' and self.owner:
            self.status = 'ASSIGNED'

        if self.status == 'CLOSED':
            # unset priority for closed tickets
            self.priority = None
        
        if not self.priority and self.status != 'CLOSED':
            max = Ticket.objects.all().aggregate(n=Max('priority'))
            self.priority = max['n'] + 1
        
        super(Ticket, self).save()

    def __unicode__(self):
        return '(#{id}) {title}'.format(**self.__dict__)

    def get_status_description(self):
        if self.status == 'CLOSED':
            return 'Closed (%s)' % self.get_closed_reason_display()
        return self.get_status_display()

    def get_priority_change_description(self, field, old):
        w = old.priority > self.priority and 'raised' or 'lowered'
        return '%s priority to *%s*' % (w, self.priority)


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='attachments')
    attachment = models.FileField(upload_to="attachments")
    
    def __unicode__(self):
        return os.path.basename(self.attachment.name)

