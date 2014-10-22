from django.conf.urls import patterns, include, url
from lights.views import switch_socket, socket_list, holding_page, sockets, switch_boiler, thermostat, makeachoice, catcannon, velux
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ('^$', makeachoice ),
    (r'^admin/', include(admin.site.urls)),
    (r'^switchsocket/(\w+)/(\d{1,2})/(\d{1,2})/(\w+)/$', switch_socket ),
    (r'^switchboiler/(\w+)/$', switch_boiler ),
    (r'^thermostat/$', thermostat ),
    (r'^thermostat/(required)/(\S+)/$', thermostat ),
    (r'^thermostat/(damoclesrepair)/$', thermostat ),
    (r'^socketlist/(toggle)/$', socket_list ),
    (r'^catcannon/(\w+)/$', catcannon ),
    (r'^velux/(\w+)/$', velux ),
    (r'^socketlist/(correct)/$', socket_list ),
)


