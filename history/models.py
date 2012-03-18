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

    @classmethod
    def from_auth_user(cls, user):
        u = cls()
        if hasattr(user, '_wrapped'):
            user = user._wrapped
        u.__dict__ = user.__dict__
        return u

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
    
    def get_old(self):
        """
        Retrieves the pre-save object from the database
        """
        Model = self.__class__
        try:
            return Model.objects.get(pk=self.pk)
        except Model.DoesNotExist:
            return None

    def has_changes(self):
        """
        Checks unsaved object against current database version
        for changes
        """
        changes = self.get_changes()
        return changes is not None and len(changes) > 0
    
    def log_changes(self, user, event=None):
        """
        Logs any unsaved object changes in the history log. Must be called before
        the .save() method.
        """
        if not event and not user:
            raise ValueError('You must provide either a user or an event object')
        if not event:
            event = Event(object=self)
        event.user = HistoryUser.from_auth_user(user)
        if not self.pk:
            return
        changes = self.get_changes()
        if changes:
            event.save()
            for change in changes:
                Change.objects.create(event=event, description=change)
            return event

    def get_changes(self):
        """
        Get a list of change descriptions of unsaved object
        """
        old = self.get_old()
        new = self
        changes = []
        for field in self._meta.fields:
            func = getattr(self, 'get_{}_change_description'.format(field.name), None)
            if func is None:
                func = self.get_change_description
            if getattr(old, field.name, None) != getattr(new, field.name, None):
                description = func(field, old)
                if description:
                    changes.append(description)
        return changes

    def get_change_description(self, field, old):
        old_value = getattr(old, field.name, None)
        new_value = getattr(self, field.name, None)
        if len(str(new_value)) > 50:
            return 'changed {}'.format(field.verbose_name)
        if old_value is None:
            old_value = '(None)'
        if old_value == '':
            old_value = '(Empty)'
        return 'changed {} from *{}* to *{}*'.format(field.verbose_name, old_value, new_value)
    
    @property
    def changes(self):
        """
        Returns a queryset of changes on this object
        """
        return Change.objects.filter(event__object_id=self.pk)

    @property
    def comments(self):
        """
        Returns a queryset of comments on this object
        """
        return Comment.objects.filter(event__object_id=self.pk)
