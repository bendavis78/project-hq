from django.conf import settings
pfx = 'TASKBOARD_'

SPRINT_DAYS = getattr(settings, '%sSPRINT_DAYS' % pfx, 14)
SPRINT_START_WEEKDAY = getattr(settings, '%sSTART_WEEKDAY' % pfx, 0)
SPRINT_OFFSET = getattr(settings, '%sSPRINT_OFFSET' % pfx, 0)
SPRINT_VELOCITY =  getattr(settings, '%sSPRINT_VELOCITY' % pfx, 0)
