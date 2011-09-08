from django.db import models
from django.contrib.auth.models import User, Group
from orderable.models import OrderableModel
from tagging.fields import TagField
from clients.models import Project

class TaskManager(models.Manager):
    def for_sprint(self):
        qs = self.get_query_set()
        return qs

class TaskUser(User):
    class Meta:
        proxy = True

    def __unicode__(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        if self.first_name:
            return self.first_name
        return self.username

class Task(OrderableModel):
    priority = models.IntegerField(null=True, editable=False)
    project = models.ForeignKey(Project)
    team = models.ForeignKey(Group)
    owner = models.ForeignKey(TaskUser, null=True, blank=True)
    description = models.TextField()
    effort = models.IntegerField()
    deadline = models.DateField(null=True,blank=True)
    completed = models.DateField(null=True,blank=True)
    blocked = models.BooleanField()
    tags = TagField()

    ordering_field = 'priority'

    class Meta:
        ordering = ['-completed','priority']

    def __unicode__(self):
        return 'Task %s' % self.id
    
    @property
    def status(self):
        if self.sprint == 0:
            return 'CURRENT'
        else:
            return 'BACKLOG'

    @property
    def sprint(self):
        from . import utils
        if self.status == 'UNPLANNED':  
            return None
        return utils.get_task_sprint(self)

class TeamStrengthAdjustment(models.Model):
    team = models.ForeignKey(Group)
    start_date = models.DateField()
    end_date = models.DateField()
