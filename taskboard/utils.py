from django.core.cache import cache
from datetime import datetime, timedelta
from taskboard import models
from taskboard import settings
import math

def calculate_sprints():
    if cache.get('task_sprints'):
        return cache.get('task_sprints', 300)

    velocity = settings.SPRINT_VELOCITY
    task_sprints = {}
    sprint = 0
    sprint_points = 0

    for task in models.Task.objects.filter(completed__isnull=True).order_by('priority'):
        if task.effort + sprint_points > velocity:
            sprint += 1
            sprint_points = 0
        task_sprints[task] = sprint
        sprint_points += task.effort
    
    cache.set('task_sprints', task_sprints)
    return task_sprints

def get_task_sprint(task):
    task_sprints = calculate_sprints()
    return task_sprints.get(task, None) 

def get_sprint_date(num=0):
    """
    Calculates the start date of the current sprint
    """
    today = datetime.today()
    # We start with the first day of the year as a reference point
    ref_date = datetime(today.year, 1, 1)
    ref_date += timedelta((settings.SPRINT_START_WEEKDAY-ref_date.weekday()) % 7)
    ref_date += timedelta(days=settings.SPRINT_OFFSET)
    days = (datetime.today() - ref_date).days
    num_sprints = math.floor(days / settings.SPRINT_DAYS) + num
    return ref_date + timedelta(days=(settings.SPRINT_DAYS*num_sprints))
