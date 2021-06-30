"""hotf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from . import views

urlpatterns = [
    path('', views.makeachoice),
    path('admin/', admin.site.urls),
    path('thermostat/', views.thermostat),
    path('thermostat/status', views.thermostat),
    path('thermostat/static', views.thermostat),
    path('thermostat/<str:modify>/', views.thermostat),
    path('thermostat/<str:modify>/<str:modify_value>/', views.thermostat),
    path('catcannon/<str:switch_onoroff>/', views.catcannon),
    path('velux/<str:openclosestate>/', views.velux),
    path('holiday/status',views.holiday),
    path('holiday/<str:modify>/<str:modify_value>/', views.holiday),
    path('holiday/',views.holiday),
    path('bork/<int:device>/<int:onoffstate>/', views.bork ),
    path('shellybork/<int:device>/<str:onoffstate>/<int:brightness>/', views.shellybork ),
    path('checkinwt/<str:device>/<str:temp_or_voltage>/<str:reading>/', views.wireless_sensor ),
    path('waterboost/<str:water_req>/<int:boosted_time>/', views.waterboost ),
    path('', include('schedule.urls')),
]
