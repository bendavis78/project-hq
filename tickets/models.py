from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from django.conf import settings
from tagging.fields import TagField
from clients.models import Project
from orderable.models import OrderableModel
from history.models import HistoryModel, Event
from datetime import datetime
import os

TICKET_STATUS_CHOICES = (
    ('NEW', 'New'),
    ('ASSIGNED', 'Assigned'),
    ('ACKNOWLEGED', 'Acknowleged'),
    ('SCHEDULED', 'Scheduled'),
    ('FEEDBACK', 'Feedback'),
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
    
    @classmethod
    def from_auth_user(cls, user):
        u = cls()
        if hasattr(user, '_wrapped'):
            user = user._wrapped
        u.__dict__ = user.__dict__
        return u

class Ticket(OrderableModel, HistoryModel, models.Model):
    submitted_by = models.ForeignKey(TicketUser, related_name='submitted_tickets')
    submitted_date = models.DateTimeField(default=datetime.today, editable=False)
    priority = models.IntegerField(null=True, editable=False, db_index=True)
    project = models.ForeignKey(Project)
    title = models.CharField(max_length=250)
    status = models.CharField(max_length=15, choices=TICKET_STATUS_CHOICES, default='NEW')
    closed_reason = models.CharField(max_length=15, choices=TICKET_CLOSED_REASONS, blank=True)
    owner = models.ForeignKey(TicketUser, null=True, blank=True, related_name='owned_tickets')
    due_date = models.DateField(null=True, blank=True)
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

    
    def get_last_activity(self):
        events = self.events.order_by('-date')
        if not events.count() > 0:
            return Event(date=self.submitted_date, user_id=self.submitted_by.id, id=0)
        return events[0]

    @property
    def warnings(self):
        warnings = {}

        # check last activity date
        date = self.get_last_activity().date
        age = (datetime.today() - date).seconds / 3600.
        hours = dict(settings.TICKETS_ACTIVITY_WARNING_HOURS).get(self.status)
        if hours and age >= hours:
            warnings['last_activity'] = 'Last activity was on {}'.format(date)

        if self.due_date and self.due_date < datetime.today().date():
            warnings['due_date'] = 'Ticket was due on {}'.format(self.due_date)

        return warnings

    def is_past_due(self):
        return self.due_date and self.due_date <= datetime.today()

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='attachments')
    attachment = models.FileField(upload_to="attachments")
    
    def __unicode__(self):
        return os.path.basename(self.attachment.name)

