from django.db import models
from django.db.models.query import QuerySet
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

STATUS_CHOICES = (
    ('NOT_SCHEDULED', 'Not scheduled'),
    ('BACKLOG', 'Backlog'),
    ('NOT_STARTED', 'Not Started'),
    ('STARTED', 'Started'),
    ('BLOCKED', 'Blocked'),
    ('FINISHED', 'Finished'),
)

class TaskFilterMixin(object):
    def current(self):
        return self.filter(iteration=0)
    def backlog(self):
        return self.filter(status='PLANNED').exclude(self.for_iteration(0))

class TaskQuerySet(TaskFilterMixin, QuerySet):
    """
    A QuerySet that provides filters specifc to tasks
    """
    def _filter_or_exclude(self, negate, *args, **kwargs):
        status = kwargs.pop('status', None)
        iteration = kwargs.pop('iteration', None)
        qs = super(TaskQuerySet, self)._filter_or_exclude(negate, *args, **kwargs)
        if iteration is not None:
            from taskboard import utils
            try:
                tasks = utils.get_iterations()[iteration]
            except KeyError:
                return self.none()
            return qs.filter(pk__in=tasks)
        if status == 'SCHEDULED':
            return qs.filter(priority__isnull=False, finished_date__isnull=False)
        if status == 'NOT_SCHEDULED':
            return qs.exclude(status='SCHEDULED')
        if status == 'FINISHED':
            return qs.filter(finished_date__isnull=False)
        if status == 'STARTED':
            return qs.filter(started_date__isnull=False, priority__isnull=False)
        if status == 'BLOCKED':
            return qs.filter(blocked=True, finished_date__isnull=True)
        if status == 'NOT_STARTED':
            return qs.current().filter(started_date__isnull=True)
        if status == 'BACKLOG':
            return qs.backlog()
        return qs
    
class TaskManager(TaskFilterMixin, models.Manager):
    def get_query_set(self):
        return TaskQuerySet(self.model, using=self._db)

class TaskUser(User):
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


class Task(OrderableModel, HistoryModel, models.Model):
    """
    Task is the meat of the taskboard module. Each task is assigned a priority.
    If priority is None and is not marked as finished, the task is "unplanned".
    The task's iteration is automatically calculated based on the tasks effort 
    setting. If a task is blocked, something is keeping it from being completed.
    """
    priority = models.IntegerField(null=True, editable=False)
    ticket = models.OneToOneField(Ticket,null=True,blank=True)
    project = models.ForeignKey(Project)
    team = models.ForeignKey(Group)
    owner = models.ForeignKey(TaskUser, null=True, blank=True, default=0)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    effort = models.IntegerField(choices=EFFORT_CHOICES)
    due_date = models.DateField(null=True,blank=True)
    started_date = models.DateField('Started date', null=True, blank=True)
    finished_date = models.DateField('Finished date', null=True,blank=True)
    blocked = models.BooleanField()
    tags = TagField()

    ordering_field = 'priority'

    objects = TaskManager()

    class Meta:
        ordering = ['priority']

    def __unicode__(self):
        return self.title
    
    @property
    def status(self):
        # order matters here
        if self.finished_date:
            return 'FINISHED'
        if self.priority is None:
            return 'NOT_SCHEDULED'
        if self.blocked:
            return 'BLOCKED'
        if self.started_date:
            return 'STARTED'
        if self.iteration == 0:
            return 'NOT_STARTED'
        return 'BACKLOG'
    
    def get_status_description(self):
        return dict(STATUS_CHOICES)[self.status]

    @property
    def iteration(self):
        from taskboard import utils
        return utils.get_task_iteration(self)

    @property
    def iteration_date(self):
        from taskboard import utils
        return utils.get_iteration_date(self.iteration)

    @property
    def iteration_end_date(self):
        from taskboard import utils
        return utils.get_iteration_end_date(self.iteration)

    def save(self):
        # Note: The sprint cache is updated on each save by the post_save 
        # signal within listeners.py
        if self.ticket and self.ticket.status in ('NEW', 'ASSIGNED', 'ACKNOWLEGED'):
            if not self.priority:
                self.ticket.status = 'ACKNOWLEGED'
            else:
                self.ticket.status = 'SCHEDULED'
            self.ticket.save()
        if self.finished_date is not None:
            self.priority = None
        return super(Task, self).save()

    @models.permalink
    def get_absolute_url(self):
        return ('taskboard_details', (self.pk,))

class TeamStrengthAdjustment(models.Model):
    team = models.ForeignKey(Group)
    start_date = models.DateField()
    end_date = models.DateField()
    percentage = models.DecimalField(max_digits=2, decimal_places=2)
