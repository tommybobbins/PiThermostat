from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'thermocalc.views.home', name='home'),
    # url(r'^thermocalc/', include('thermocalc.foo.urls')),
       (r'^schedule/', include('schedule.urls')),
       (r'^admin/', include(admin.site.urls)),
)
#       (r'^accounts/login/$',  login),
#       (r'^accounts/logout/$',  logout),
