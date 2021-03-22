from django.db import models
from django.contrib import admin
from django import forms

class ESP8266(models.Model):
    LOCATION_CHOICES = (
        ('inside','inside'),
        ('outside','outside'),
    )
    name = models.CharField(max_length=30)
    macaddress = models.CharField(max_length=17, default='00:11:22:33:44:55')
    multiplier = models.SmallIntegerField(help_text='The number indicates the important of heating (e.g. Cellar = 1, Living Room = 5)')
    location = models.CharField(max_length=10, choices=LOCATION_CHOICES, default='inside')
    expirytime = models.SmallIntegerField(default=3600,help_text='Time to expire temperatures in seconds if the device is powered off')
    def __unicode__(self):
        return self.name

class ESP8266Admin(admin.ModelAdmin):
    list_display = ('name','macaddress','multiplier','location','expirytime')

admin.site.register(ESP8266,ESP8266Admin)

class WirelessTemp(models.Model):
    LOCATION_CHOICES = (
        ('inside','inside'),
        ('outside','outside'),
    )
    name = models.CharField(max_length=30)
    macaddress = models.CharField(max_length=4, default='CC')
    multiplier = models.SmallIntegerField(help_text='The number indicates the important of heating (e.g. Cellar = 1, Living Room = 5)')
    location = models.CharField(max_length=10, choices=LOCATION_CHOICES, default='inside')
    expirytime = models.SmallIntegerField(default=3600,help_text='Time to expire temperatures in seconds if the device is powered off')
    def __unicode__(self):
        return self.name

class WirelessTempAdmin(admin.ModelAdmin):
    list_display = ('name','macaddress','multiplier','location','expirytime')

admin.site.register(WirelessTemp,WirelessTempAdmin)
