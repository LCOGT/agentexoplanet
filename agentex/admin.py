from agentex.models import Target, Event, Datapoint, DataSource, Badge, Achievement, DataCollection,Decision,CatSource, Observer
from agentex.views import averagecals
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext

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
    
def allcalibrators_check(request,planetid):
    event = Event.objects.get(id=planetid)
    normcals,dates,ids,cats = averagecals(event.name,0)
    #a = averagecals(event.name,0)
    #print len(a)
    title = 'Check calibrators for %s' % event.title
    return render_to_response('admin/agentex/allcalibrators.html',{'calibrators':normcals,'dates':dates,'calids':ids,'cats':cats,'title':title},context_instance=RequestContext(request))
    
def calibrator_check(request,planetid,calid):
    planet = Event.objects.get(id=clid)
    n = 0
    data,points,sources = my_data(o,code)
    dc = DataCollection.objects.filter(person=o.user,planet=planet)
    if dc.count() > n:
        n = range(0,dc.count())
        cats = []
        for order in n:
            dc0 = dc.filter(calid=order)[0]
            c = points.filter(pointtype='C',coorder=dc0)[:1]
            valid = c[0].coorder.display
            coll = {'order' : order,
                    'name'  : c[0].coorder.source,
                    'valid' : valid,
                    }
            cats.append(coll)
    return render_to_response('admin/agentex/calibrator.html',context_instance=RequestContext(request))
    
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