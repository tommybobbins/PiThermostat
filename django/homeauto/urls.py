from django.conf.urls import patterns, include, url
from lights.views import switch_socket, socket_list, holding_page, sockets, switch_boiler, thermostat, makeachoice
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ('^$', makeachoice ),
    (r'^admin/', include(admin.site.urls)),
    (r'^switchsocket/(\d{1,2})/(\d{1,2})/(\w+)/$', switch_socket ),
    (r'^switchboiler/(\w+)/$', switch_boiler ),
    (r'^thermostat/$', thermostat ),
    (r'^thermostat/(required)/(\d+\.\d+)/$', thermostat ),
    (r'^thermostat/(increment|decrement)/(\d\.\d)/$', thermostat ),
    (r'^socketlist/(toggle)/$', socket_list ),
    (r'^socketlist/(correct)/$', socket_list ),
    (r'^schedule/', include('schedule.urls')),
)


