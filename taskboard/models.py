from datetime import datetime
from django.core.exceptions import ValidationError
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

TASK_TYPES = (
    ('FEATURE', 'Feature'),
    ('MILESTONE', 'Milestone'),
    ('BUG', 'Bug'),
    ('CHORE', 'Chore'),
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
            return qs.filter(pk__in=[t.pk for t in tasks])
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

class Team(Group):
    velocity = models.PositiveIntegerField(default=0)
    velocity_strategy = models.PositiveIntegerField(default=4,
            help_text='Number of past iterations used to calculate suggested velocity')
    
    def get_suggested_velocity(self):
        #TODO
        pass


class Task(OrderableModel, HistoryModel, models.Model):
    """
    Task is the meat of the taskboard module. Each task is assigned a priority.
    If priority is None and is not marked as finished, the task is "unplanned".
    The task's iteration is automatically calculated based on the tasks effort 
    setting. If a task is blocked, something is keeping it from being completed.
    """
    type = models.CharField(max_length=20, choices=TASK_TYPES, default='FEATURE')
    priority = models.IntegerField(null=True, editable=False)
    ticket = models.OneToOneField(Ticket,null=True,blank=True)
    project = models.ForeignKey(Project)
    team = models.ForeignKey(Team)
    owner = models.ForeignKey(TaskUser, null=True, blank=True, default=0)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    effort = models.IntegerField(choices=EFFORT_CHOICES, null=True)
    due_date = models.DateField(null=True,blank=True)
    started_date = models.DateTimeField(null=True, blank=True)
    finished_date = models.DateTimeField(null=True, blank=True)
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
        if self.type != 'FEATURE':
            self.points = 0
        return super(Task, self).save()

    def clean(self):
        if self.effort is None and self.status != 'NOT_SCHEDULED':
            raise ValidationError('Effort cannot be null on scheduled or finished tasks.')

    @property
    def warnings(self):
        warnings = {}
        if self.status != 'FINISHED' and self.due_date and self.due_date < datetime.today().date():
            warnings['due_date'] = 'Task deadline was on {}'.format(self.due_date)
        if self.status in ('BACKLOG', 'BLOCKED'):
            if self.due_date and self.due_date < self.iteration_date:
                warnings['due_date'] = 'Task deadline is {}'.format(self.due_date)
        return warnings

    @models.permalink
    def get_absolute_url(self):
        return ('taskboard_details', (self.pk,))

class TeamStrengthAdjustment(models.Model):
    team = models.ForeignKey(Team, related_name='strength_adjustments')
    start_date = models.DateField()
    end_date = models.DateField()
    percentage = models.PositiveIntegerField(
            help_text='The percentage of team\'s velocity')

    def __unicode__(self):
        return '{0}: {1:%b %-d} - {2:%b %-d} @ {3}'.format(
            self.team, 
            self.start_date,
            self.end_date,
            self.percentage
        )
