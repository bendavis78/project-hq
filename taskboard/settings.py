from django.conf import settings
pfx = 'TASKBOARD_'

ITERATION_CACHE_KEY = getattr(settings, '%sITERATION_CACHE_KEY' % pfx, 'calculated_tasks')
ITERATION_DAYS = getattr(settings, '%sITERATION_DAYS' % pfx, 14)
ITERATION_START_WEEKDAY = getattr(settings, '%sSTART_WEEKDAY' % pfx, 0)
ITERATION_OFFSET = getattr(settings, '%sITERATION_OFFSET' % pfx, 0)
ITERATION_VELOCITY =  getattr(settings, '%sITERATION_VELOCITY' % pfx, 0)
