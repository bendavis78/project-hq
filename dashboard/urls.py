from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('dashboard.views',
    url(r'^', 'index', name='dashboard-index'),
)
