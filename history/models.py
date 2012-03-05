from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class HistoryUser(User):
    class Meta:
        proxy = True

    def __unicode__(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        if self.first_name:
            return self.first_name
        return self.username

class Event(models.Model):
    object = generic.GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    date = models.DateTimeField(default=datetime.today)
    user = models.ForeignKey(HistoryUser)

class Comment(models.Model):
    event = models.OneToOneField(Event, related_name='comment')
    message = models.TextField()

class Change(models.Model):
    event = models.ForeignKey(Event, related_name='changes')
    description = models.CharField(max_length=250)

class HistoryModel(models.Model):
    events = generic.GenericRelation(Event)
    class Meta:
        abstract = True
    
    def log_changes(self, event):
        """
        Logs any changes to the object in the history log. Must be called before
        the .save() method. Requires implementation of the get_changes() method.
        """
        if not self.pk:
            return
        changes = []
        Model = self.__class__
        old = Model.objects.get(pk=self.pk)
        changes = self.get_changes(old)
        if changes:
            for change in changes:
                Change.objects.create(event=event, description=change)
            return event

    def get_changes(self, old):
        return []

