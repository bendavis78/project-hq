from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('tickets.views',
    url(r'^$', 'index', name='tickets-index'),
    url(r'^archive/$', 'archive', name='tickets-archive'),
    url(r'^create/$', 'create', name='tickets-create'),
    url(r'^(?P<pk>\d+)/$', 'detail', name='ticket-details'),
    url(r'^(?P<pk>\d+)/edit/$', 'update', name='tickets-edit'),
)
