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
        sc = AverageSet.objects.get(planet=self.planet, settype='S').data
        bg = AverageSet.objects.get(planet=self.planet, settype='B').data
        return cals,sc,bg,time,ids,cats

    def final(self):
        normvals = AverageSet.objects.get(planet=self.planet,settype='F').data
        std = AverageSet.objects.get(planet=self.planet,settype='E').data
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
