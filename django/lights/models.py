from django.db import models
from django.contrib import admin
#from lights.models import Socket

class Socket(models.Model):
    LOCATION_CHOICES = (
        ('attic','attic'),
        ('cellar','cellar'),
    )
    PLUG_CHOICES = (
        ('energenie','energenie'),
        ('homeeasy','homeeasy'),
    )
    name = models.CharField(max_length=30)
    set_id = models.SmallIntegerField(verbose_name='Set ID', help_text='Which set the plug belongs to 1 or 2')
    plug_id = models.SmallIntegerField(verbose_name='Plug number', help_text='Number printed on the plug e.g. 3')
    switch_state = models.BooleanField(help_text='On is Checked, Off is Unchecked' ,default=False)
    lastcheckin = models.DateTimeField(blank=True, null=True,help_text='Leave blank. Will be populated when last switched on')
    total_times_fired = models.IntegerField(help_text='Number of times toggled',blank=True,null=True,default=0)
    location = models.CharField(max_length=10, choices=LOCATION_CHOICES, default='cellar')
    plug_type = models.CharField(max_length=60, choices=PLUG_CHOICES, default='energenie')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Sockets"

class SocketAdmin(admin.ModelAdmin):
    list_display = ('name','plug_id','set_id','switch_state','location')

admin.site.register(Socket,SocketAdmin)

