'''
Citizen Science Portal: App containing Agent Exoplant and Show Me Stars for Las Cumbres Observatory Global Telescope Network
Copyright (C) 2014-2015 LCOGT

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''
from agentex.models import Event, AverageSet, Decision, Datapoint, DataSource
import agentex as ax

####
#import matplotlib.pyplot as plt
####

from django.contrib.auth.models import User
from django.db.models import Count, Avg
from datetime import datetime
from calendar import timegm
from numpy import array,nan_to_num, vstack, apply_along_axis, mean, var, sqrt,average, r_, linspace

from django.conf import settings

class Dataset(object):
    def __init__(self , planetid=None,userid=None):
        try:
            self.planet = Event.objects.get(slug=planetid)
        except:
            self.planet = None
        try:
            self.user = User.objects.get(username=userid)
        except:
            self.user = None
        try:
            self.target = Target.objects.get(name=self.planet.title[:-1])
        except:
            self.target = None
    def calibrators(self):
        sc = AverageSet.objects.filter(planet=self.planet, settype='S')[0].data
        bg = AverageSet.objects.filter(planet=self.planet, settype='B')[0].data
        return cals,sc,bg,time,ids,cats
    def final(self):
        normvals = AverageSet.objects.filter(planet=self.planet,settype='F')[0].data
        std = AverageSet.objects.filter(planet=self.planet,settype='E')[0].data
        sources = DataSource.objects.filter(event=self.planet).order_by('timestamp')
        #myvals = ax.views.myaverages(self.planet,self.user)
        n = 0
        data = []
        if len(normvals) == self.planet.numobs :
            for i,s in enumerate(sources):
                line = {
                        'id'        : "%i" % s.id,
                        'date'      : s.timestamp.isoformat(" "),
                        'datestamp' : timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,
                        'data'      : {
                                        'mean' : normvals[i],
                                        'std'  : std[i],
                                        'mine' : 'null',#myvals[i],
                            },
                        }
                data.append(line)
        else:
            data = None
        return data
    def my_data(self):
        if self.user:
            data = []
            sources = DataSource.objects.filter(event=self.planet).values_list('id','timestamp').order_by('timestamp')
            points  = Datapoint.objects.filter(data__event=self.planet,user=self.user)
            sc = dict(points.filter(pointtype='S').values_list('data__id','value'))
            bg = dict(points.filter(pointtype='B').values_list('data__id','value'))
            cals = points.filter(pointtype='C').values_list('data__id','value').order_by('coorder')
            for d in sources:
                cal = [c[1] for c in cals if int(c[0]) == d[0]]
                line = {
                        'id'        : "%i" % d[0],
                        'date'      : d[1].isoformat(" "),
                        'datestamp' : timegm(d[1].timetuple())+1e-6*d[1].microsecond,
                        'data'      : { 'source' : None,
                                        'background' :  None,
                                        'calibrator' :  cal,
                                    },
                        }
                try:
                    line['data']['source'] = [sc[d[0]]]
                except:
                    line['data']['source'] = 'null'
                try:
                    line['data']['background'] = [bg[d[0]]]
                except:
                    line['data']['background'] = 'null'
                data.append(line)
            return data,points
        else:
            self.error = "No user specified"
            return False
        # Produce final lightcurve from the average data sets
        # calibs = []
        # mypoints = []
        # calslist = []
        # ti = 0.
        # # assume data which has AverageSet forms part of a complete set
        # # People and their sources who have Dips in the select planet
        # decs = Decision.objects.values_list('person','source').filter(value='D', current=True, planet=self.planet, source__datacollection__display=True).annotate(Count('source'))
        # peoplelst,sourcelst,tmp = zip(*decs)
        # people = set(peoplelst)
        # sources = set(sourcelst)
        # #catsources = Decision.objects.values_list('source',flat=True).filter(value='D', current=True, planet=self.planet)
        # if decs.count() > 0:
        #     vals = Datapoint.objects.filter(data__event=self.planet,user__in=people)
        #     sourceave = vals.filter(pointtype='S').values_list('data').annotate(mean=Avg('value')).order_by('data__timestamp')
        #     bgave = vals.filter(pointtype='B').values_list('data').annotate(mean=Avg('value')).order_by('data__timestamp')
        #     sc_ave = zip(*sourceave)
        #     bg_ave = zip(*bgave)
        #     sc = array(sc_ave[1])
        #     bg = array(bg_ave[1])
        #     sets = AverageSet.objects.filter(planet=self.planet,star__in=sources)
        #     for s in sets:
        #         calslist.append(s.data)
        #     numsuper = sets.count()
        #     if settings.LOCAL_DEVELOPMENT: print "Number of supercals for %s : %s" % (self.planet.title,numsuper)
        #     # sc_set = AverageSet.objects.filter(planet=self.planet, settype='S')[0]
        #     # bg_set = AverageSet.objects.filter(planet=self.planet, settype='B')[0]
        #     # sc = array(sc_set.data)
        #     # bg = array(bg_set.data)
        #     calstack = vstack(calslist)
        #     cc = (sc-bg)/(calstack-bg)
        #     n = 0
        #     sourcelist = list(sources)
        #     calibs.append(cc.tolist())
        #     norm_a = lambda a: mean(r_[a[:3],a[-3:]])
        #     cala = vstack(calibs)
        #     norms = apply_along_axis(norm_a, 1, cala)
        #     dim = len(cala)
        #     norm1 = cala/norms.reshape(dim,1)
        #     for c in norm1:
        #         filename = 'media/transit/%s-%s.png' % (self.planet.name,sourcelist[n])
        #         plt.plot(linspace(0,len(sc),len(sc)),c, lw=2)
        #         plt.savefig(filename)
        #         plt.close()
        #         n+=1
        #     norm_alt = mean(norm1,axis=0)
        #     variance = var(norm1,axis=0)
        #     std = sqrt(variance)
        #     fz = list(norm_alt)
        #     mycals = myaverages(self.planet,self.user)
        #     nodata = True
        #     return numsuper,fz,mycals,list(std),nodata
        # else:
        #     print "No average sets"
