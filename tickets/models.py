from django.db import models
from django.db.models import F, Max
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

class Ticket(OrderableModel):
    submitted_by = models.ForeignKey(TicketUser, related_name='submitted_tickets')
    priority = models.IntegerField(null=True, editable=False, db_index=True)
    project = models.ForeignKey(Project)
    title = models.CharField(max_length=250)
    status = models.CharField(max_length=15, choices=TICKET_STATUS_CHOICES, default='NEW')
    closed_reason = models.CharField(max_length=15, choices=TICKET_CLOSED_REASONS, blank=True)
    owner = models.ForeignKey(TicketUser, null=True, blank=True, related_name='owned_tickets')
    due_date = models.DateField(null=True, blank=True)
    submitted_date = models.DateTimeField(default=datetime.today, editable=False)
    task = models.ForeignKey(Task, null=True, blank=True, editable=False)
    description = models.TextField()
    tags = TagField()
    
    ordering_field = 'priority'

    class Meta:
        ordering = ('priority','-submitted_date')
    
    def convert_to_task(self):
        if self.task:
            raise TaskExists("A task already exists for this ticket")
    
    @models.permalink
    def get_absolute_url(self):
        return ('ticket_details', (self.pk,))
   
    def save(self):
        if self.status == 'NEW' and self.owner:
            self.status = 'ASSIGNED'

        if self.status == 'CLOSED':
            # unset priority for closed tickets
            self.priority = None

        if self.priority:
            current = Ticket.objects.get(pk=self.pk)
            if current.priority > self.priority:
                # when moving down, increment those between the move
                Ticket.objects.filter(priority__lt=current.priority, 
                        priority__gte=self.priority).update(priority=F('priority')+1)
            elif current.priority < self.priority:
                # when moving up, decrement those between the move
                Ticket.objects.filter(priority__gt=current.priority, 
                        priority__lte=self.priority).update(priority=F('priority')-1)
        elif self.status != 'CLOSED':
            max = Ticket.objects.all().aggregate(n=Max('priority'))
            self.priority = max['n'] + 1
        
        super(Ticket, self).save()

    def __str__(self):
        return '(#{id}) {title}'.format(**self.__dict__)

    def get_status_description(self):
        if self.status == 'CLOSED':
            return 'Closed (%s)' % self.get_closed_reason_display()
        return self.get_status_display()

    def log_changes(self, event):
        """
        Logs any changes to the ticket in the ticket log. Must be called before
        the .save() method.
        """
        if not self.pk:
            return
        changes = []
        old = Ticket.objects.get(pk=self.pk)
        new = self
        if old.status != new.status:
            changes.append('changed status to *%s*' % new.get_status_description())
        if old.title != new.title:
            changes.append('changed title to *%s*' % new.title)
        if old.priority != new.priority:
            w = old.priority > new.priority and 'raised' or 'lowered'
            changes.append('%s priority to *%s*' % (w, new.priority))
        if old.owner != new.owner:
            changes.append('changed owner to *%s*' % new.owner)
        if old.due_date != new.due_date:
            changes.append('changed due date to *%s*' % new.due_date)
        if old.description != new.description:
            changes.append('updated description')
        if old.tags != new.tags:
            changes.append('changed tags to *%s*' % self.tags)
        
        if changes:
            for change in changes:
                change = TicketChange.objects.create(description=change)
                event.changes.add(change)
            return event

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='attachments')
    attachment = models.FileField(upload_to="attachments")
    
    def __unicode__(self):
        return os.path.basename(self.attachment.name)

class TicketEvent(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='events')
    date = models.DateTimeField(default=datetime.today)
    user = models.ForeignKey(User)

class TicketComment(models.Model):
    event = models.OneToOneField(TicketEvent, related_name='comment')
    message = models.TextField()

class TicketChange(models.Model):
    event = models.ForeignKey(TicketEvent, related_name='changes')
    description = models.CharField(max_length=250)
