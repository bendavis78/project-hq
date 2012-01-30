from django.conf.urls.defaults import patterns, url, include
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'dashboard.views.index'),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^tickets/', include('tickets.urls')),
    url(r'^taskboard/', include('taskboard.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', 
            {'template_name':'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
            {'template_name':'logout.html'}, name='logout'),
)

# Serve media statically using django
# Should only be used in development environments
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
