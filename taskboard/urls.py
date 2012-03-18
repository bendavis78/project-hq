from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('taskboard.views',
    url(r'^$', 'index', name='taskboard_index'),
    url(r'^list-items/$', 'list_items', name='taskboard_list_items'),
    url(r'^create/$', 'create', name='taskboard_create'),
    url('^action/$', 'action', name='taskboard_action'),
    url(r'^(?P<pk>\d+)/$', 'detail', name='taskboard_details'),
    url(r'^(?P<pk>\d+)/edit/$', 'update', name='taskboard_edit'),
    url(r'^(?P<pk>\d+)/delete/$', 'delete', name='taskboard_delete'),
    url(r'^(?P<pk>\d+)/move/(?P<to>(last|unscheduled|\d+))/$', 'move', name='taskboard_move'),
    url(r'^(?P<pk>\d+)/start/$', 'start', name='taskboard_task_start'),
    url(r'^(?P<pk>\d+)/finish/$', 'finish', name='taskboard_task_finish'),
    url(r'^(?P<pk>\d+)/set-effort/$', 'set_effort', name='taskboard_task_set_effort'),
    url(r'^set-team-strength/$', 'set_team_strength', name='taskboard_team_strength'),
)
