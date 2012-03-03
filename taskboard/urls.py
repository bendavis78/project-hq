from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('taskboard.views',
    url(r'^$', 'index', name='taskboard_index'),
    url(r'^create/$', 'create', name='taskboard_create'),
    url(r'^(?P<pk>\d+)/$', 'detail', name='taskboard_details'),
    url(r'^(?P<pk>\d+)/edit/$', 'update', name='taskboard_edit'),
    url(r'^(?P<pk>\d+)/move/(?P<to>\d+)/$', 'move', name='taskboard_move'),
)
