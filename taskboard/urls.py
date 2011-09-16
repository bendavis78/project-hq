from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('taskboard.views',
    url(r'^', 'index', name='taskboard_index'),
)

