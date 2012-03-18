from django.template import Library
from taskboard import utils
register = Library()

@register.simple_tag
def get_iteration_points(iteration):
    return utils.get_iteration_points(iteration)

@register.inclusion_tag('taskboard/includes/iteration_point_breakdown.html')
def iteration_point_breakdown(iteration):
    return {
        'breakdown': utils.get_iteration_point_breakdown(iteration)
    }

@register.inclusion_tag('taskboard/includes/status_action_btn.html')
def status_action_btn(task):
    c = {'task': task}
    if task.status == 'NOT_STARTED':
        c.update({'action': 'start', 'label': 'Start'})
    if task.status == 'STARTED':
        c.update({'action': 'finish', 'label': 'Finish'})
    return c
