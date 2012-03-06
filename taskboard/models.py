from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User, Group
from tagging.fields import TagField
from clients.models import Project
from orderable.models import OrderableModel
from history.models import HistoryModel
from tickets.models import Ticket

EFFORT_CHOICES = (
    (0, '0'),
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (5, '5'),
    (8, '8')
)

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

class Task(OrderableModel, HistoryModel, models.Model):
    priority = models.IntegerField(null=True, editable=False)
    ticket = models.OneToOneField(Ticket,null=True,blank=True)
    project = models.ForeignKey(Project)
    team = models.ForeignKey(Group)
    owner = models.ForeignKey(TaskUser, null=True, blank=True)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    effort = models.IntegerField(choices=EFFORT_CHOICES)
    due_date = models.DateField(null=True,blank=True)
    completed = models.DateField(null=True,blank=True)
    blocked = models.BooleanField()
    tags = TagField()

    ordering_field = 'priority'

    objects = TaskManager()

    class Meta:
        ordering = ['-completed','priority']

    def __unicode__(self):
        return self.title
    
    @property
    def status(self):
        if self.completed:
            return 'COMPLETED'
        if self.sprint == 0:
            return 'CURRENT'
        return 'BACKLOG'
    
    def get_status_description(self):
        return {
            'COMPLETED': 'Completed',
            'CURRENT': 'In progress',
            'BACKLOG': 'Backlog',
        }[self.status]

    @property
    def sprint(self):
        from taskboard import utils
        return utils.get_task_sprint(self)

    @property
    def sprint_date(self):
        from taskboard import utils
        return utils.get_sprint_date(self.sprint)

    @property
    def sprint_end_date(self):
        from taskboard import utils
        return utils.get_sprint_end_date(self.sprint)

    def save(self):
        # any time a task is changed, delete sprint cache
        cache.delete('task_sprints')
        return super(Task, self).save()

    @models.permalink
    def get_absolute_url(self):
        return ('taskboard_details', (self.pk,))

class Milestone(models.Model):
    name = models.CharField(max_length=150)
    date = models.DateField()    

    def __unicode__(self):
        return '{} - {}'.format(self.date, self.name)

class TeamStrengthAdjustment(models.Model):
    team = models.ForeignKey(Group)
    start_date = models.DateField()
    end_date = models.DateField()
    percentage = models.DecimalField(max_digits=2, decimal_places=2)
