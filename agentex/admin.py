from agentex.models import Target, Event, Datapoint, DataSource, Badge, Achievement, DataCollection,Decision,CatSource, Observer, AverageSet
from agentex.views import photometry, calibrator_data, admin_averagecals
from django.contrib import admin
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils import simplejson

class DatapointAd(admin.ModelAdmin):
    list_display = ['taken','data','pointtype','user','xpos','ypos','value','coorder','get_source']
    list_filter = ['pointtype']
    def get_source(self,obj):
        return '%s' % obj.coorder.source
    get_source.allow_tags = True
    get_source.short_description = 'Cat Source'
    
class DCAdmin(admin.ModelAdmin):
    list_display = ['planet','person','calid','display','complete']
    list_filter = ['display','complete','planet','person']

class DecAdmin(admin.ModelAdmin):
    list_display = ['value','person','planet','taken','source']
    list_filter = ['planet','value']
class CatAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['final']
    list_display = ['name','data','get_planet','final']
    def get_planet(self,obj):
        return '%s' % obj.data.event.title
    get_planet.allow_tags = True
    get_planet.short_description = 'Planet'
      
class DSAdmin(admin.ModelAdmin):
    list_filter = ['event','target']
    list_display = ['timestamp','event','target']
    
class EventAdmin(admin.ModelAdmin):
    list_display = ['title','name','start','midpoint','end','numobs','xpos','ypos','enabled']    
class TargetAdmin(admin.ModelAdmin):
    list_display = ['name','ra','dec','period','rstar','mass','ap','inclination']
    
class SetAdmin(admin.ModelAdmin):
    list_display = ['planet','star','settype']
    
def allcalibrators_check(request,planetid):
    # Uses and SQL statement to try to speed up the query for averaging data points
    e = Event.objects.filter(id=planetid)[0]
    normcals,dates,ids,cats = admin_averagecals(e.name,0)
    c = simplejson.dumps(cats)
    # return normcals,stamps,[int(i) for i in ids],cats
    title = 'Check calibrators for %s' % e.title
    return render_to_response('admin/agentex/allcalibrators.html',{'calibrators':normcals,
                                                                    'title':title,
                                                                    'planetid':planetid,
                                                                    'dates':dates,
                                                                    'calids':[int(i) for i in ids],
                                                                    'cats':c},context_instance=RequestContext(request))
    
def calibrator_check(request,planetid,calid):
    planet = Event.objects.get(id=planetid)
    dcs = DataCollection.objects.filter(source__id=calid)
    if request.POST:
        people = request.POST.getlist('user')
        dcs.update(display=False)  
        include = request.POST.get('include','none')
        cs = CatSource.objects.filter(id=calid)
        if include == 'false':
            cs.update(final=False)
        elif include == 'true':
            cs.update(final=True)
        elif include == 'none':
            dcup = dcs.filter(person__username__in=people)
            dcup.update(display=True)
    data,times,people = calibrator_data(calid,planet.name)
    include = dcs.filter(person__username__in=people).values_list('display',flat=True)
    resp = {'data'       : data,
            'timestamps' : times,
            'people'     : people,
            'include'    : list(include),
            }
    return HttpResponse(simplejson.dumps(resp,indent=2),mimetype='application/javascript')
    
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
admin.site.register(AverageSet,SetAdmin)