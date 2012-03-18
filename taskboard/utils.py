from django.core.cache import cache
from django.db.models import Q
from datetime import date, timedelta
from taskboard import models
from taskboard import settings
import math

def get_calculated_tasks():
    if cache.get(settings.ITERATION_CACHE_KEY):
        return cache.get(settings.ITERATION_CACHE_KEY, 3600)
    return calculate_iterations()

def clear_iteration_cache():
    cache.delete(settings.ITERATION_CACHE_KEY)

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
    return sum([t.effort for t in tasks])

def get_iteration_point_breakdown(iteration):
    breakdown = []
    tasks = get_iterations()[iteration]
    for team in models.Team.objects.all():
        team_points = sum([t.effort for t in tasks if t.team == team])
        breakdown.append({
            'team': team,
            'velocity': get_team_velocity(team, iteration),
            'points': team_points,
        })
    return breakdown

def get_team_velocity(team, iteration):
    i_start, i_end = get_iteration_dates(iteration)
    filters = {
        'start_date__lt': i_end,
        'end_date__gt': i_start
    }
    adjustments = team.strength_adjustments.filter(**filters)
    # break iteration into days, get daily reduction percentages
    deduction = 0
    num_days = (i_end - i_start).days + 1
    for i in range(0, num_days):
        day = i_start + timedelta(days=i)
        for a in adjustments:
            if day >= a.start_date and day <= a.end_date:
                deduction += (team.velocity / float(num_days)) * float(a.percentage)
    return int(round(team.velocity - deduction))


def calculate_iterations():
    """
    This is the meat of the task system. Iterations are dynamic, meaning that
    the iteration for a given task is calculated on-the-fly (with a 1hr cache).
    This allows for more flexibility, fewer database hits, and less chance of
    corruption of data when changing iteration settings such as velocity and
    team strength.

    Each team has it's own velocity, and each task is assigned to a team. All
    projects follow the base iteration length (ITERATION_DAYS), which is
    typically one week. The only reason a project should need longer iterations
    is for the purpose of planning milestones, in which case you can just limit
    the dates for which you are able to create milestone tasks.
    """
    calculated_tasks = {}

    for team in models.Team.objects.all():
        iteration = 0
        iteration_points = 0
        velocity = get_team_velocity(team, iteration)
        dates = get_iteration_dates(iteration)
        # include finished tasks within current iteration
        planned_tasks = models.Task.objects.filter(Q(priority__isnull=False) |
                                                   Q(finished_date__range=dates),
                                                   effort__isnull=False)

        for task in planned_tasks.order_by('finished_date', 'priority'):
            if task.effort + iteration_points > velocity:
                iteration += 1
                iteration_points = 0
                velocity = get_team_velocity(team, iteration)
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
    today = date.today() 
    # We start with the first day of the year as a reference point
    ref_date = date(today.year, 1, 1)
    ref_date += timedelta((settings.ITERATION_START_WEEKDAY-ref_date.weekday()) % 7)
    ref_date += timedelta(days=settings.ITERATION_OFFSET)
    days = (date.today() - ref_date).days
    num_iterations = math.floor(days / settings.ITERATION_DAYS) + num
    return ref_date + timedelta(days=(settings.ITERATION_DAYS*num_iterations))

def get_iteration_end_date(num=0):
    date = get_iteration_date(num)
    return date + timedelta(days=settings.ITERATION_DAYS-1)

def get_iteration_dates(num=0):
    return (get_iteration_date(num), get_iteration_end_date(num))
