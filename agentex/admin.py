from citsciportal.agentex.models import Target, Event, Datapoint, DataSource, Badge, Achievement, DataCollection,Decision,CatSource, Observer
from django.contrib import admin

class DatapointAd(admin.ModelAdmin):
    list_display = ['taken','data','pointtype','user','xpos','ypos','value','coorder','get_source']
    list_filter = ['pointtype']
    def get_source(self,obj):
        return '%s' % obj.coorder.source
    get_source.allow_tags = True
    get_source.short_description = 'Cat Source'
    
class DCAdmin(admin.ModelAdmin):
    list_display = ['planet','person','calid']

class DecAdmin(admin.ModelAdmin):
    list_display = ['value','person','planet','taken','source']
    list_filter = ['planet','value']
class CatAdmin(admin.ModelAdmin):
    search_fields = ['name']
      
class DSAdmin(admin.ModelAdmin):
    list_filter = ['event','target']
    list_display = ['timestamp','event','target']
    
class EventAdmin(admin.ModelAdmin):
    list_display = ['title','name','start','midpoint','end','numobs','xpos','ypos','enabled']    
class TargetAdmin(admin.ModelAdmin):
    list_display = ['name','ra','dec','period','rstar','mass','ap','inclination']
    
admin.site.register(Target, TargetAdmin)
admin.site.register(Event,EventAdmin)
admin.site.register(Datapoint, DatapointAd)
admin.site.register(DataSource,DSAdmin)
admin.site.register(Badge)
admin.site.register(Decision,DecAdmin)
admin.site.register(Achievement)
admin.site.register(Observer)
admin.site.register(CatSource,CatAdmin)
admin.site.register(DataCollection,DCAdmin)