from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tickets.views',
    url(r'^$', 'index', name='tickets_index'),
    url(r'^archive/$', 'archive', name='tickets_archive'),
    url(r'^create/$', 'create', name='tickets_create'),
    url('^action/$', 'action', name='tickets_action'),
    url(r'^(?P<pk>\d+)/$', 'detail', name='ticket_details'),
    url(r'^(?P<pk>\d+)/edit/$', 'update', name='tickets_edit'),
    url(r'^(?P<pk>\d+)/move/(?P<to>\d+)/$', 'move', name='tickets_move'),
)
