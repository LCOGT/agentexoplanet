from django.contrib import admin
from citsciportal.showmestars.models import Event

class EventAd(admin.ModelAdmin):
    list_display = ['name','start','end','site']


admin.site.register(Event,EventAd)
