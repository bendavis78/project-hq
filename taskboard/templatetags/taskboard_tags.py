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
