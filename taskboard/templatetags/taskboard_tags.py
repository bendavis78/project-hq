from django.template import Library
from taskboard import utils
register = Library()

@register.simple_tag
def get_iteration_points(iteration):
    return utils.get_iteration_points(iteration)
