import json
from django.utils.encoding import smart_unicode
from django.core.serializers import serialize
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION
from django.db.models import Count,Avg,Min,Max,Variance, Q, Sum
from django.contrib import messages
from django.db import connection
import urllib2
from xml.dom.minidom import parse
from math import sin,acos,fabs,sqrt
from numpy import *
from astropy.io import fits 
from datetime import datetime,timedelta
from calendar import timegm
from time import mktime
from math import floor,pi,pow
from itertools import chain
from numpy import array,nan_to_num

from django.contrib.auth.models import User
from agentex.models import Target, Event, Datapoint, DataSource, DataCollection,CatSource, Decision, Achievement, Badge, Observer, AverageSet
from agentex.models import decisions
from agentex.forms import DataEntryForm, RegisterForm, CommentForm,RegistrationEditForm
import agentex.dataset as ds

from django.conf import settings
from agentex.agentex_settings import planet_level

def calibrator_data(calid,code):
    data = []
    sources, times = zip(*DataSource.objects.filter(event__name=code).values_list('id','timestamp').order_by('timestamp'))
    points  = Datapoint.objects.filter(data__in=sources)
    #points.filter(pointtype='C').values('data__id','user','value')
    people = Decision.objects.filter(source__id=calid,planet__name=code,value='D',current=True).values_list('person__username',flat=True).distinct()
    norm = dict((key,0) for key in sources)
    for pid in people:
        cal = []
        sc = dict(points.filter(user__username=pid,pointtype='S').values_list('data__id','value'))
        bg = dict(points.filter(user__username=pid,pointtype='B').values_list('data__id','value'))
        c = dict(points.filter(user__username=pid,pointtype='C',coorder__source__id=calid).values_list('data__id','value'))
        sc_norm = dict(norm.items() + sc.items())
        bg_norm = dict(norm.items() + bg.items())
        c_norm = dict(norm.items() + c.items())
        #print sc_norm,bg_norm,c_norm
        for v in sources:
            try:
                cal.append((sc_norm[v]- bg_norm[v])/(c_norm[v] - bg_norm[v]))
            except:
                cal.append(0)
        data.append(cal)
    return data,[timegm(s.timetuple())+1e-6*s.microsecond for s in times],list(people)

def average_combine(measurements,averages,ids,star,category,progress,admin=False):
    if progress['done'] < progress['total']:
        ave_measurement = averages.filter(star=star,settype=category)
        if ave_measurement.count() > 0:
            ## Find the array indices of my values and replace these averages
            ave = array(ave_measurement[0].data)
            mine = zip(*measurements.values_list('data','value'))
            try:
                my_ids = [ids.index(x) for x in mine[0]]
                ave[my_ids] = mine[1]
            except Exception, e:
                print e
            return ave
        else:
            return array([])
    elif progress['done'] == progress['total']:
        mine = array(measurements.values_list('value',flat=True))
        return mine
    elif not progress:
        print "No progress was passed"
        return array([])
    else:
        print "Error - too many measurements: %s %s" % (measurements.count() , numobs)
        return array([])

def calibrator_averages(code,person=None,progress=False):
    cals = []
    cats = []
    planet = Event.objects.get(name=code)
    sources = list(DataSource.objects.filter(event=planet).order_by('timestamp').values_list('id','timestamp'))
    ids,stamps = zip(*sources)
    if person:
        ## select calibrator stars used, excluding ones where ID == None, i.e. non-catalogue stars
        dc = DataCollection.objects.filter(~Q(source=None),person=person,planet=planet).order_by('calid')
        ## Measurement values only for selected 'person'
        dps = Datapoint.objects.filter(data__event=planet,user=person).order_by('data__timestamp')
    else:
        # select calibrator stars used, excluding ones where ID == None, i.e. non-catalogue stars
        dc = DataCollection.objects.filter(~Q(source=None),planet=planet).order_by('calid')
        ## Measurement values only for selected 'person'
        dps = Datapoint.objects.filter(data__event=planet).order_by('data__timestamp')
    averages = AverageSet.objects.filter(planet=planet)
    if person:
        # Make a combined list of source values
        measurements = dps.filter(pointtype='S')
        sc = average_combine(measurements,averages,ids,None,'S',progress)
        # Make a combined list of background values
        measurements = dps.filter(pointtype='B')
        bg = average_combine(measurements,averages,ids,None,'B',progress)
    else:
        sc = array(averages.filter(star=None,settype='S')[0].data)
        bg = array(averages.filter(star=None,settype='B')[0].data)
    # Make a combined list of all calibration stars used by 'person'
    for calibrator in dc:
        if person:
            measurements = dps.filter(pointtype='C',coorder=calibrator)
            ave = average_combine(measurements,averages,ids,calibrator.source,'C',progress)
        else:
            ave_cal = averages.filter(star=calibrator,settype='C')
            if ave_cal.count() > 0:
                ave = array(ave_cal[0].data)
            else:
                ave = array([])
        if ave.size > 0:
            cals.append(ave)
            try:
                if person:
                    decvalue = Decision.objects.filter(source=calibrator.source,person=person,planet=planet,current=True)[0].value
                else:
                    decvalue = Decision.objects.filter(source=calibrator.source, planet=planet,current=True)[0].value
            except:
                decvalue ='X'
            cat_item = {'sourcename':calibrator.source.name,'catalogue':calibrator.source.catalogue}
            cat_item['decsion'] = decvalue
            cat_item['order'] = str(calibrator.calid)
            cats.append(cat_item)
    return cals,sc,bg,stamps,ids,cats

def photometry(code,person,progress=False,admin=False):
    
    # Empty lists to store normalised calibrators and maximum values
    normcals = []
    maxvals = []

    # Call in averages
    cals,sc,bg,times,ids,cats = calibrator_averages(code,person,progress)
    
    indexes = [int(i) for i in ids]
    #sc = array(sc)
    #bg = array(bg)     
    
    # Iterate over every calibrator
    for cal in cals:
        if len(cal) == progress['total']:
            #### Do not attempt to do the photmetry where the number of calibrators does not match the total        
                # Determine calibrated flux from source
                val = (sc - bg)/(cal-bg)
                # Determine maximum flux from source
                maxval = mean(r_[val[:3],val[-3:]])
                # Append to maxvals
                maxvals.append(maxval)
                # Normalise the maxval
                norm = val/maxval
                #Append the normalised value
                normcals.append(list(norm))
            # Find my data and create unix timestamps
        unixt = lambda x: timegm(x.timetuple())+1e-6*x.microsecond
        iso = lambda x: x.isoformat(" ")
        stamps = map(unixt,times)
        dates = map(iso,times)
    if admin:
        return normcals,stamps,indexes,cats
    return cals,normcals,list(sc),list(bg),dates,stamps,indexes,cats