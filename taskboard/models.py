from django.db import models
from orderable.models import OrderableModel

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

class TaskManager(models.Manager):
    def for_sprint(self):
        qs = self.get_query_set()
        return qs

class Task(OrderableModel):
    priority = models.IntegerField(null=True)
    project = models.ForeignKey(Project)
    description = models.TextField()
    effort = models.IntegerField()
    completed = models.DateField(null=True,blank=True)
    blocked = models.BooleanField()
    icebox = models.BooleanField()

    ordering_field = 'priority'

    class Meta:
        ordering = ['-completed','priority']

    def __unicode__(self):
        return 'Task %s' % self.id
    
    @property
    def sprint(self):
        from . import utils
        return utils.get_task_sprint(self)
 
#class SprintHistory(models.Model):
#    start_date = models.DateField()
#    end_date = models.DateField()
#    velocity = models.IntegerField()
#    completed_points = models.IntegerField()
