from django.conf.urls import patterns, include, url
from lights.views import switch_socket, socket_list, holding_page, sockets, thermostat, makeachoice, catcannon, velux, current, holiday
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ('^$', makeachoice ),
    (r'^admin/', include(admin.site.urls)),
    (r'^switchsocket/(\w+)/(\d{1,2})/(\d{1,2})/(\w+)/$', switch_socket ),
    (r'^thermostat/$', thermostat ),
    (r'^thermostat/(required)/(\S+)/$', thermostat ),
    (r'^thermostat/(damoclesrepair)/$', thermostat ),
    (r'^thermostat/(android)/$', thermostat ),
    (r'^holiday/$', holiday ),
    (r'^holiday/(temp)/(\S+)/$', holiday ),
    (r'^holiday/(days)/(\S+)/$', holiday ),
    (r'^calendar/', include('happenings.urls', namespace='calendar')),
    (r'^current/$', current ),
    (r'^socketlist/(toggle)/$', socket_list ),
    (r'^catcannon/(\w+)/$', catcannon ),
    (r'^velux/(\w+)/$', velux ),
    (r'^socketlist/(correct)/$', socket_list ),
)


