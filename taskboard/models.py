from django.db import models
from django.contrib.auth.models import User
from orderable.models import OrderableModel
from tagging.fields import TagField

class Client(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Project(models.Model):
    client = models.ForeignKey(Client)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return '[%s] %s' % (self.client.name, self.name)

    class Meta:
        ordering = ['client', 'name']

class Team(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(User)

    def __unicode__(self):
        return self.name

class TaskManager(models.Manager):
    def for_sprint(self):
        qs = self.get_query_set()
        return qs

class Task(OrderableModel):
    priority = models.IntegerField(null=True)
    project = models.ForeignKey(Project)
    team = models.ForeignKey(Team)
    description = models.TextField()
    effort = models.IntegerField()
    deadline = models.DateField(null=True,blank=True)
    completed = models.DateField(null=True,blank=True)
    blocked = models.BooleanField()
    icebox = models.BooleanField()
    tags = TagField()

    ordering_field = 'priority'

    class Meta:
        ordering = ['-completed','priority']

    def __unicode__(self):
        return 'Task %s' % self.id
    
    @property
    def sprint(self):
        from . import utils
        return utils.get_task_sprint(self)

class TeamStrengthAdjustment(models.Model):
    team = models.ForeignKey(Team)
    start_date = models.DateField()
    end_date = models.DateField()
