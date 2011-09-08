from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'dashboard.views.index'),
    (r'^dashboard/', include('dashboard.urls')),
    (r'^tickets/', include('tickets.urls')),
    (r'^taskboard/', include('taskboard.urls')),
    (r'^admin/', include(admin.site.urls)),
)

# Serve media statically using django
# Should only be used in development environments
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
