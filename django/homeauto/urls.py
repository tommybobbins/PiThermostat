from django.conf.urls import *
from lights.views import switch_socket, socket_list, holding_page, sockets, thermostat, makeachoice, catcannon, velux, current, holiday, esp_sensor, wireless_sensor
from django.contrib import admin

urlpatterns = [ 
    url('^$', makeachoice ),
    url(r'^admin/', admin.site.urls),
    url(r'^switchsocket/url(\w+)/url(\d{1,2})/url(\d{1,2})/url(\w+)/$', switch_socket ),
    url(r'^thermostat/$', thermostat ),
    url(r'^thermostat/url(required)/url(\S+)/$', thermostat ),
    url(r'^thermostat/url(damoclesrepair)/$', thermostat ),
    url(r'^thermostat/url(android)/$', thermostat ),
    url(r'^thermostat/url(refresh)/url(\S+)/$', thermostat ),
    url(r'^holiday/$', holiday ),
    url(r'^holiday/url(temp)/url(\S+)/$', holiday ),
    url(r'^holiday/url(days)/url(\S+)/$', holiday ),
    url(r'^holiday/url(boost)/url(\S+)/$', holiday ),
    url(r'^calendar/', include('happenings.urls', namespace='calendar')),
    url(r'^current/$', current ),
    url(r'^checkin/url(\S+)/temperature/url(\S+)/$', esp_sensor ),
    url(r'^checkinwt/url(\S+)/url(\S+)/url(\S+)/$', wireless_sensor ),
    url(r'^socketlist/url(\S+)/$', socket_list ),
    url(r'^catcannon/url(\w+)/$', catcannon ),
    url(r'^velux/url(\w+)/$', velux ),
]


