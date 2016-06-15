from django.conf.urls import patterns, include, url
from lights.views import switch_socket, socket_list, holding_page, sockets, thermostat, makeachoice, catcannon, velux, current, holiday, esp_sensor, wireless_sensor
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
    (r'^thermostat/(refresh)/(\S+)/$', thermostat ),
    (r'^holiday/$', holiday ),
    (r'^holiday/(temp)/(\S+)/$', holiday ),
    (r'^holiday/(days)/(\S+)/$', holiday ),
    (r'^calendar/', include('happenings.urls', namespace='calendar')),
    (r'^current/$', current ),
    (r'^checkin/(\S+)/temperature/(\S+)/$', esp_sensor ),
    (r'^checkinwt/(\S+)/(\S+)/(\S+)/$', wireless_sensor ),
    (r'^socketlist/(toggle)/$', socket_list ),
    (r'^catcannon/(\w+)/$', catcannon ),
    (r'^velux/(\w+)/$', velux ),
    (r'^socketlist/(correct)/$', socket_list ),
)


