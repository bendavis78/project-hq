from django.core.cache import cache
from datetime import datetime, timedelta
from taskboard import models
from taskboard import settings
import math

def get_calculated_tasks():
    if cache.get(settings.ITERATION_CACHE_KEY):
        return cache.get(settings.ITERATION_CACHE_KEY, 3600)
    return calculate_iterations()

def get_iterations():
    iterations = {}
    tasks = get_calculated_tasks()
    for task, i in tasks.iteritems():
        if iterations.get(i, None) is None:
            iterations[i] = []
        iterations[i].append(task)
    return iterations

def get_iteration_points(iteration):
    tasks = get_iterations()[iteration]
    total = 0
    for task in tasks:
        total += task.effort
    return total
    
def calculate_iterations():
    velocity = settings.ITERATION_VELOCITY
    calculated_tasks = {}
    iteration = 0
    iteration_points = 0
    
    planned_tasks = models.Task.objects.filter(priority__isnull=False)
    for task in planned_tasks.order_by('priority'):
        if task.effort + iteration_points > velocity:
            iteration += 1
            iteration_points = 0
        calculated_tasks[task] = iteration
        iteration_points += task.effort
    
    cache.set(settings.ITERATION_CACHE_KEY, calculated_tasks)
    return calculated_tasks

def get_task_iteration(task):
    calculated_tasks = get_calculated_tasks()
    return calculated_tasks.get(task, None) 

def get_iteration_date(num=0):
    """
    Calculates the start date of the current iteration
    """
    today = datetime.today()
    # We start with the first day of the year as a reference point
    ref_date = datetime(today.year, 1, 1)
    ref_date += timedelta((settings.ITERATION_START_WEEKDAY-ref_date.weekday()) % 7)
    ref_date += timedelta(days=settings.ITERATION_OFFSET)
    days = (datetime.today() - ref_date).days
    num_iterations = math.floor(days / settings.ITERATION_DAYS) + num
    return ref_date + timedelta(days=(settings.ITERATION_DAYS*num_iterations))

def get_iteration_end_date(num=0):
    date = get_iteration_date(num)
    return date + timedelta(days=settings.ITERATION_DAYS)
