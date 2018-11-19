'''
Citizen Science Portal: App containing Agent Exoplanet and Show Me Stars for Las Cumbres Observatory Global Telescope Network
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

from astropy.io import fits
from astropy.table import Table
from calendar import timegm
from datetime import datetime,timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.serializers import serialize
from django.db import connection
from django.db.models import Count,Avg,Min,Max,Variance, Q, Sum
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.urls import reverse
from django.utils.encoding import smart_text
from itertools import chain
from math import floor,pi,pow,sin,acos,fabs,sqrt
from time import mktime
import json
import logging
import numpy as np

from agentex.models import *
from agentex.models import decisions
from agentex.forms import DataEntryForm
import agentex.dataset as ds

from agentex.agentex_settings import planet_level
from agentex.datareduc import *

guestuser = 2

logger = logging.getLogger('agentex')

def home(request):
    ''' Render the Front page of citizen science portal '''
    return render(request, 'index.html', {})


def index(request):
    #return render_to_response('agentex/index.html', context_instance=RequestContext(request))
    return render(request, 'agentex/index.html', {})

def target(request):
    data = []
    events = Event.objects.filter(enabled=True)
    for e in events:
        if (request.user.is_authenticated):
            person = request.user
            completed = Datapoint.objects.filter(user=person, data__event__name=e,pointtype='S').count()
        else:
            person = guestuser
            completed = 0
        points =Datapoint.objects.filter(user=person,pointtype='S')
        try:
            level = planet_level[e.name]
        except:
            level = None
        line = {'event':e,'points':points,'completed':completed,'level':level}
        data.append(line)
    #return render_to_response('agentex/target.html', {'data':data},context_instance=RequestContext(request))
    return render(request, 'agentex/target.html', {'data':data})

@login_required
def addvalue_post(request, person, code):

    # Writes current observer to variable o
    o = person
    # Tracks progress of observer
    progress = checkprogress(person,code)

    ####### Form data has been submitted
    x = []
    y = []
    nocals = request.POST.get('calibrators','1')
    setting = request.POST.get('entrytype','')
    # Only update the user's preference if they change it
    if (setting == 'manual' and o[0].dataexploreview == True):
        o.update(dataexploreview=False)
        messages.success(request, "Setting changed to use manual view")
        entrymode = 'M'
    elif (setting == 'dataexplorer' and o[0].dataexploreview == False):
        o.update(dataexploreview=True)
        messages.success(request, "Setting changed to use web view")
        entrymode = 'W'
    else:
        entrymode = 'N'
    id = request.POST.get('dataid','')
    form = DataEntryForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        ind = {'source':'S','bg':'B'}
        reduced = 0
        update = request.POST.get('update','')
        counts = list()
        for i in ind:
            value = float(cd[i+'counts'])
            x.append(cd[i+'xpos'])
            y.append(cd[i+'ypos'])
            counts.append(value)
        for vari in range(1,int(nocals)+1):
            cali = str(vari)
            value = request.POST.get('cal'+cali+'counts','')
            x.append(request.POST.get('cal'+cali+'xpos',''))
            y.append(request.POST.get('cal'+cali+'ypos',' '))
            counts.append(float(value))
        pointsum = {'bg' :  '%.2f' % counts[0], 'sc' : '%.2f' % counts[1], 'cal' : counts[2:]}
        if (len(x) < 3 or len(y) < 3):
            messages.warning(request,'Please submit calibration, blank sky and source apertures.')
            url = reverse('agentex.views.addvalue',args= [DataSource.objects.get(id=id).event.name])
            return HttpResponseRedirect(url)
        x = map(float,x)
        y = map(float,y)
        coords = zip(x,y)
        dataid = request.POST.get('dataid','')
        resp = savemeasurement(person,pointsum,coords,dataid,entrymode)
        messages.add_message(request, resp['code'], resp['msg'])
        if webin == False:
            url = "%s?%s" % (reverse('agentex.views.addvalue',args= [DataSource.objects.get(id=id).event.name]),"input=manual")
        else:
            url = reverse('agentex.views.addvalue',args= [DataSource.objects.get(id=id).event.name])
         #messages.success(request, "Measurement successfully added")
        return HttpResponseRedirect(url)
    else:
        #return render_to_response('agentex/dataentry.html', {'data':DataSource.objects.get(id=id),'form':form,'data_url':settings.DATA_URL}, context_instance=RequestContext(request))
        return render(request, 'agentex/dataentry.html', {'data':DataSource.objects.get(id=id),'form':form,'data_url':settings.DATA_URL})


@login_required
def addvalue_nopost(request, person, code):
    nextcal = request.GET.get('next',False)
    # Call DataEntryForm from agentex.forms
    form = DataEntryForm()

    o = person
    progress = checkprogress(person,code)
    ############ This condition is active when a user edits the frame
    # Find the data sources for the given code
    source = DataSource.objects.filter(event__name=code)
    length = source.count()

    ###### Has the user selected to use the web interface?
    ###### Default for anonymous is always web interface
    # If statement to check if user is guest
    if (person != guestuser):
        try:
            webin = o[0].dataexploreview
        except:
            webin = True
    else:
        webin = True
    least_coords = leastmeasured(code)

    # Pull out data user has viewed and exclude them from the list of possible candidates
    ds = Datapoint.objects.values_list('data',flat=True).filter(data__event__name=code,user=person,pointtype='S')
    input = request.GET.get('input',False)
    id = request.GET.get('dataid',False)
    # If an ID is specified return the frame, as long as the person has made measurements of it
    if id:
        dnext = False
        #### If anonymous user tell them they cannot edit points
        if person == guestuser:
            messages.warning(request,'You cannot edit points unless you are logged in')
            try:
                url = reverse('agentex.views.addvalue',args= [DataSource.objects.get(id=id).event.name])
                return HttpResponseRedirect(url)
            except:
                raise Http404
        mycalibs = []
        ##### The page is being displayed with data for editing
        points = Datapoint.objects.filter(data__id=id,user=person)
        if nextcal=='cal':
            dp = Datapoint.objects.filter(pointtype='S',user=person,data__id=id)
            dd = dp[0].data.timestamp
            ds = Datapoint.objects.filter(pointtype='S',user=person,data__timestamp__gt=dd).order_by('data__timestamp')
            if ds.count() > 0:
                dnext = ds[0].data
        d = DataSource.objects.filter(id=id)[0]
        otherpoints = Datapoint.objects.filter(~Q(user=person),pointtype='C',data=d)
        cals = Datapoint.objects.values_list('xpos','ypos','radius').filter(data=d,pointtype='C').order_by('coorder__calid')
        calibs = []
        if cals:
            for c in cals:
                calibs.append({'x' : int(c[0]) , 'y' : int(c[1]), 'r' : int(c[2])})
        source = points.filter(pointtype='S')[:1]
        bg = points.filter(pointtype='B')[:1]
        #### If there are no results, the person is hacking the query string. Return a fresh frame
        if (source.count() == 0 or bg.count() == 0):
            url = reverse('agentex.views.addvalue',args= [code])
            return HttpResponseRedirect(url)
        cal = points.filter(pointtype='C').order_by('coorder__calid')
        for c in cal:
            line = {'x' :c.xpos,'y' : c.ypos}
            mycalibs.append(line)
        ### If more cals have been placed on other frames add these to this frame
        max_cal = Datapoint.objects.filter(pointtype='C',user=person).aggregate(max=Max('coorder__calid'))['max']
        if max_cal+1 > cal.count():
            for order in range(cal.count(),max_cal+1):
                dp = Datapoint.objects.filter(pointtype='C',user=person,coorder__calid=order,data__event__name=code)
                if dp.count() > 0:
                    line = {'x': dp[0].xpos, 'y':dp[0].ypos}
                    # Add to the mycalibs array
                    mycalibs.append(line)
        coords = { 'source': {'x' :source[0].xpos,'y' : source[0].ypos},
                 'cal'  : mycalibs,
                 'bg'  : {'x' :bg[0].xpos,'y' : bg[0].ypos},
                 'radius' : source[0].radius,
                 'id'  : id,
                 'numcals' : len(mycalibs),
                 }
        messages.info(request, "Updating measurement")
        '''
        return render_to_response('agentex/dataentry.html',{'data':d,
                                                                'next':dnext,
                                                                'points':coords,
                                                                'update':True,
                                                                'webinput':webin,
                                                                'progress':progress,
                                                                'form':form,
                                                                'calibrators':calibs,
                                                                'least_data':least_coords,
                                                                'data_url':settings.DATA_URL},
                                context_instance=RequestContext(request))
        '''
        return render(request, 'agentex/dataentry.html', {'data':d,
                                                                'next':dnext,
                                                                'points':coords,
                                                                'update':True,
                                                                'webinput':webin,
                                                                'progress':progress,
                                                                'form':form,
                                                                'calibrators':calibs,
                                                                'least_data':least_coords,
                                                                'data_url':settings.DATA_URL})
    else:
        ######## User is being given a new frame not editing data
        o = person
        progress = checkprogress(person,code)
        complete = 0
        if  (progress['done'] >= progress['total'] and person != guestuser):
            ####### No new data can be provided because the user has come to the end
            complete = 1
            numplanets = DataCollection.objects.values('planet').filter(person=person,complete=True).annotate(Count('complete')).count()
            e = Event.objects.filter(name=code)[0]
            resp = achievementscheck(person,e,0,0,0,0,numplanets)

            msg = '<br />'
            for item in resp:
                if messages.SUCCESS == item['code'] :
                    msg += "<img src=\""+settings.STATIC_URL+item['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />"
                    messages.success(request,msg)
            return HttpResponseRedirect(reverse('my-graph',args=[code]))

            '''
            return render_to_response('agentex/dataentry.html',
                                    {'event': e,
                                    'complete':complete,
                                    'progress':progress,
                                    'points':Datapoint.objects.filter(user=person,pointtype='S',data__event=e).order_by('data__timestamp'),
                                    'data_url':settings.DATA_URL,
                                    'numplanets':numplanets,},
                                    context_instance=RequestContext(request))
            '''
            return render(request, 'agentex/dataentry.html', {'event': e,
                                    'complete':complete,
                                    'progress':progress,
                                    'points':Datapoint.objects.filter(user=person,pointtype='S',data__event=e).order_by('data__timestamp'),
                                    'data_url':settings.DATA_URL,
                                    'numplanets':numplanets,})
        else:
            planet = Event.objects.get(name=code)
            mylist = Datapoint.objects.filter(user=person,pointtype='S',data__event=planet).values_list('data',flat=True)
            ### if person does not have a DataCollection it is their first measurement
            if (DataCollection.objects.filter(planet=planet,person=person).count() == 0):
                d = DataSource.objects.filter(event=planet,id=planet.finder)[0]
                did = d.id
                try:
                    dold = d.id
                    first = True
                except:
                    messages.error(request,"Finderchart cannot be found")
                    raise Http404
            elif  person == guestuser:
                d = DataSource.objects.filter(event=planet).annotate(count=Count('datapoint')).order_by('-count')[0]
                did = d.id
                dold = d.id
                first = True
            else:
                try:
                    source_rank = DataSource.objects.filter(event=planet ).annotate(count=Count('datapoint') ).values_list('id','count').order_by('-count')
                    available = [x for x in source_rank if x[0] not in list(mylist)]
                    dold = Datapoint.objects.values_list('data__id',flat=True).filter(user=person,data__event=planet,pointtype='C').annotate(max =Max('coorder__calid')).order_by('-max','-taken')[0]
                # Find position in set of DataSources
                    d = available[0]
                    did = d[0]
                    first = False
                except Exception:
                    messages.error(request,"User has a data collection but no points!")
                    raise Http404
            cals = Datapoint.objects.values_list('xpos','ypos').filter(data=dold,pointtype='C',user=person).order_by('coorder__calid')
            calibs = []
            if cals:
                for c in cals:
                    calibs.append({'x' : int(c[0]) , 'y' : int(c[1])})
            otherpoints = Datapoint.objects.filter(~Q(user=person),pointtype='C',data__id=did)
            othercals = []
            if otherpoints:
                for c in otherpoints:
                    othercals.append({'x' : int(c.xpos) , 'y' : int(c.ypos),'r':int(c.radius)})
            prev = Datapoint.objects.filter(user=person,data=dold).order_by('coorder__calid')
            if first == False:
                coords = { 'source': {'x' :prev.filter(pointtype='S')[0].xpos,'y' : prev.filter(pointtype='S')[0].ypos},
                         'bg'  : {'x' :prev.filter(pointtype='B')[0].xpos,'y' : prev.filter(pointtype='B')[0].ypos},
                         'cal'  : calibs ,
                         'id'  : dold,
                         'radius' : planet.radius
                         }
            else:
                coords = False
            if person == guestuser:
                progress = {'percent'   : "0",
                            'done'      : 0,
                            'total'     : n_sources,}
            '''
            return render_to_response('agentex/dataentry.html',
                                    {'data':DataSource.objects.get(id=did),
                                    'complete':complete,
                                    'update':False,
                                    'webinput':webin,
                                    'progress':progress,
                                    'form':form,
                                    'calibrators':othercals,
                                    'points':coords,
                                    'least_data':least_coords,
                                    'data_url':settings.DATA_URL},
                                    context_instance=RequestContext(request))
            '''
            return render(request, 'agentex/dataentry.html', {'data':DataSource.objects.get(id=did),
                                    'complete':complete,
                                    'update':False,
                                    'webinput':webin,
                                    'progress':progress,
                                    'form':form,
                                    'calibrators':othercals,
                                    'points':coords,
                                    'least_data':least_coords,
                                    'data_url':settings.DATA_URL})

@login_required
def addvalue(request,code):

    # Import pdf and set trace for debug
    #import pdb; pdb.set_trace()
    # If statement to allow admin access to authenticated users
    if (request.user.is_authenticated):
        if request.user.username == 'admin':
            superuser = True
            sudo = request.GET.get('sudo','')
            if sudo:
                person = User.objects.get(id=sudo)
            else:
                person = request.user
        else:
            person = request.user
            superuser = False

    o = person
    progress = checkprogress(person,code)

    if (progress['done'] >= progress['total']):
        dcolls = DataCollection.objects.filter(person=person,planet__name=code)
        dcolls.update(complete=True)
    '''
    ###### Has the user selected to use the web interface?
    ###### Default for anonymous is always web interface
    # If statement to check if user is guest
    if (person != guestuser):
        try:
            webin = o[0].dataexploreview
        except:
            webin = True
    else:
        webin = True
    least_coords = leastmeasured(code)
    '''
    if (request.POST):
        result = addvalue_post(request, person, code)
        return result
    else:
        result = addvalue_nopost(request, person, code)
        return result

def savemeasurement(person,pointsum,coords,dataid,entrymode):
    # Only update the user's preference if they change it
    o = person
    try:
        if (entrymode == 'manual' and o[0].dataexploreview == True):
            o.update(dataexploreview=False)
            messages.success(request, "Setting changed to use manual view")
        elif (entrymode == 'dataexplorer' and o[0].dataexploreview == False):
            o.update(dataexploreview=True)
            messages.success(request, "Setting changed to use web view")
    except:
        logger.debug("Having problems with")
    mode = {'dataexplorer':'W','manual':'M'}
    pointtype = {'sc':'S','bg':'B'}
    d = DataSource.objects.filter(id=int(dataid))
    s_x = float(coords[1][0])
    s_y = float(coords[1][1])
    if d[0].id == d[0].event.finder:
        xvar = np.abs(s_x - d[0].event.xpos)
        yvar = np.abs(s_y - d[0].event.ypos)
        if (xvar > 3 or yvar > 3):
          # Remove previous values for this point
          return {'msg': 'Target marker not correctly aligned', 'code': messages.ERROR}
    xmean = 0
    ymean = 0
    # Remove previous values for this point
    oldpoints = Datapoint.objects.filter(data=d[0],user=person)
    oldpoints.delete()
    numpoints = Datapoint.objects.filter(data__event=d[0].event,user=person).count()
    datestamp = datetime.now()
    reduced = 0
    calave = 0.
    error = ''
    ### Add a datacollection for the current user
    r = d[0].event.radius
    for k,value in pointtype.iteritems():
        # Background and source
        data = Datapoint(ident=d[0].event.name,
                            user=person,
                            pointtype = value,
                            data=d[0],
                            radius=r,
                            entrymode=mode[entrymode],
                            tstamp=mktime(d[0].timestamp.timetuple())
                            )
        if k == 'sc':
            coord = coords[1]
            data.offset = 0
        elif k == 'bg':
            coord = coords[0]
            data.offset = int(np.sqrt((s_x - float(coord[0]))**2 + (s_y - float(coord[1]))**2))
        data.value= float(pointsum[k])
        data.xpos = int(float(coord[0]))
        data.ypos = int(float(coord[1]))
        data.taken=datestamp
        try:
            data.save()
        except:
            return {'msg': 'Error saving data point', 'code': messages.ERROR}
    # Slice coord data so we only have calibration stars
    coord = coords[2:]
    basiccoord = np.array(coord[:3])
    nocals = len(coord)
    sc_cal = float(pointsum['sc']) - float(pointsum['bg'])
    # Find out if means have been calculated already, if not do it for the source
    # This step can only happen if we are not at the finder frame
    if numpoints != 0 and d[0].event.finder != d[0].id:
        xmean, ymean = measure_offset(d,person,basiccoord)
        # check the source is within this tolerance too
        sc_xpos = d[0].event.xpos
        sc_ypos = d[0].event.ypos
        xvar = np.abs(np.abs(sc_xpos-s_x)-np.abs(xmean))
        yvar = np.abs(np.abs(sc_ypos-s_y)-np.abs(ymean))
        if (xvar > 5 or yvar > 5):
            # Remove previous values for this point
            oldpoints = Datapoint.objects.filter(data__id=int(dataid),user=person)
            oldpoints.delete()
            return {'msg': 'Target marker not correctly aligned', 'code': messages.ERROR}
    for i,value in enumerate(pointsum['cal']):
        xpos = int(float(coord[i][0]))
        ypos = int(float(coord[i][1]))
        newcoord = coord
        nocolls = DataCollection.objects.filter(planet=d[0].event,person=person,calid=i).count()
        if (nocolls == 0 and person != guestuser):
            ## Find closest catalogue sources
            if i > 2:
                # Add more datacollections if i is > 2 i.e. after basic 3 have been entered
                cats = CatSource.objects.filter(xpos__lt=xpos-xmean+5,ypos__lt=ypos-ymean+5,xpos__gt=xpos-xmean-5,ypos__gt=ypos-ymean-5,data__event=d[0].event)
            else:
                cats = CatSource.objects.filter(xpos__lt=xpos+5,ypos__lt=ypos+5,xpos__gt=xpos-5,ypos__gt=ypos-5,data__event=d[0].event)
            if cats:
                dcoll = DataCollection(person=person,planet=d[0].event,complete=False,calid=i,source=cats[0])
            else:
                dcoll = DataCollection(person=person,planet=d[0].event,complete=False,calid=i)
            dcoll.display = True
            dcoll.save()
        else:
            dcoll = DataCollection.objects.filter(person=person,planet=d[0].event,calid=i)[0]
        data = Datapoint(ident=d[0].event.name,
                            user=person,
                            pointtype = 'C',
                            data=d[0],
                            radius=r,
                            entrymode=mode[entrymode],
                            tstamp=mktime(d[0].timestamp.timetuple())
                            )
        data.value= float(value)
        data.xpos = xpos
        data.ypos = ypos
        data.offset = int(np.sqrt((s_x - float(coord[i][0]))**2 + (s_y - float(coord[i][1]))**2))
        data.taken=datestamp
        data.coorder = dcoll
        try:
            data.save()
        except:
            return {'msg': 'Error saving', 'code': messages.ERROR}
        calave = calave +sc_cal/(value - float(pointsum['bg']))/float(nocals)
    else:
        #resp = achievementcheck(person,d[0].event,nocals,'calibrator')
        #nomeas = Datapoint.objects.filter(data__event__name=d[0].event,user=person).values('taken').annotate(Count('taken')).count()
        nomeas = Datapoint.objects.filter(user=person).values('taken').annotate(Count('taken')).count()
        noplanet = DataCollection.objects.filter(person=person).values('planet').annotate(Count('person')).count()
        ndecs = Decision.objects.filter(person=person,current=True).count() # filter: ,planet=d[0].event
        unlock = False
        nunlock = 0
        resp = achievementscheck(person,d[0].event,nomeas,noplanet,nocals,ndecs,0)
        msg = '<br />'
        for item in resp:
            if messages.SUCCESS == item['code'] :
                msg += "<img src=\""+settings.STATIC_URL+item['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />"
                unlock = True
                nunlock += 1

        if unlock :
            if nunlock > 1 : return {'msg': 'Achievements unlocked'+msg, 'code': messages.SUCCESS}
            else : return {'msg': 'Achievement unlocked'+msg, 'code': messages.SUCCESS}
        return {'msg': 'Measurements saved', 'code': messages.SUCCESS}





def read_manual_check(request):
	if (request.POST.get('read_manual','')=='true' and request.user.is_authenticated):
		o = personcheck(request)
		resp = achievementunlock(o.user,None,'manual')
		if messages.SUCCESS == resp['code'] :
			messages.add_message(request, messages.SUCCESS, "Achievement unlocked<br /><img src=\""+settings.STATIC_URL+resp['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />")
	return HttpResponseRedirect(reverse(target))


# measurements, planets, calibrators descisions
def achievementscheck(person,planet,nmeas,nplan,ncals,ndcsn,ncomp):
    resp = []
    if person.id!=guestuser:
        if nmeas == 1 : resp.append(achievementunlock(person,planet,'measurement_1'))
        if nmeas == 5 : resp.append(achievementunlock(person,planet,'measurement_5'))
        if nmeas == 10 : resp.append(achievementunlock(person,planet,'measurement_10'))
        if nmeas == 25 : resp.append(achievementunlock(person,planet,'measurement_25'))
        if nmeas == 50 : resp.append(achievementunlock(person,planet,'measurement_50'))
        if nmeas == 100 : resp.append(achievementunlock(person,planet,'measurement_100'))
        if nmeas == 250 : resp.append(achievementunlock(person,planet,'measurement_250'))
        if nmeas == 500 : resp.append(achievementunlock(person,planet,'measurement_500'))
        if nmeas == 1000 : resp.append(achievementunlock(person,planet,'measurement_1000'))
        if nmeas == 1500 : resp.append(achievementunlock(person,planet,'measurement_1500'))
        if nmeas == 2000 : resp.append(achievementunlock(person,planet,'measurement_2000'))
        if ncals >= 3 : resp.append(achievementunlock(person,planet,'calibrator_3'))
        if ncals >= 5 : resp.append(achievementunlock(person,planet,'calibrator_5'))
        if ncals >= 10 : resp.append(achievementunlock(person,planet,'calibrator_10'))
        if ncals >= 15 : resp.append(achievementunlock(person,planet,'calibrator_15'))
        if ncals >= 25 : resp.append(achievementunlock(person,planet,'calibrator_25'))
        if nplan == 1 : resp.append(achievementunlock(person,planet,'planet_1'))
        if nplan == 2 : resp.append(achievementunlock(person,planet,'planet_2'))
        if nplan == 3 : resp.append(achievementunlock(person,planet,'planet_3'))
        if nplan == 4 : resp.append(achievementunlock(person,planet,'planet_4'))
        if nplan == 5 : resp.append(achievementunlock(person,planet,'planet_5'))
        if nplan == 6 : resp.append(achievementunlock(person,planet,'planet_6'))
        if nplan == 7 : resp.append(achievementunlock(person,planet,'planet_7'))
        if nplan == 8 : resp.append(achievementunlock(person,planet,'planet_8'))
        if nplan == 9 : resp.append(achievementunlock(person,planet,'planet_9'))
        if ndcsn >= 3 : resp.append(achievementunlock(person,planet,'lightcurve_1star'))
        if ndcsn >= 10 : resp.append(achievementunlock(person,planet,'lightcurve_2star'))
        if ncomp == 1 : resp.append(achievementunlock(person,planet,'completed_1'))
        if ncomp == 2 : resp.append(achievementunlock(person,planet,'completed_2'))
        if ncomp == 3 : resp.append(achievementunlock(person,planet,'completed_3'))
        if ncomp == 4 : resp.append(achievementunlock(person,planet,'completed_4'))
        if ncomp == 5 : resp.append(achievementunlock(person,planet,'completed_5'))
        if ncomp == 6 : resp.append(achievementunlock(person,planet,'completed_6'))
        if ncomp == 7 : resp.append(achievementunlock(person,planet,'completed_7'))
        if ncomp == 8 : resp.append(achievementunlock(person,planet,'completed_8'))
        if ncomp == 9 : resp.append(achievementunlock(person,planet,'completed_9'))

    return resp


def achievementunlock(person,planet,typea):
    # Check what badges user has to see if they deserve more
    # The planet will simply be to record where they got this achievement
    achs = Achievement.objects.filter(person=person) #,planet=planet
    badge =  Badge.objects.filter(name=typea)
    if badge.count() == 0:
        return {'msg' : 'Wrong badge code', 'code': messages.ERROR}
    if achs.filter(badge=badge).count() == 0:
        newa = Achievement(badge=badge[0],planet=planet,person=person)	# ,planet=planet
        try:
            newa.save()
            LogEntry.objects.log_action(
                user_id         = person.id,
                content_type_id = ContentType.objects.get_for_model(newa).pk,
                object_id       = newa.pk,
                object_repr     = smart_text(newa),
                action_flag     = ADDITION,
                change_message  = 'Achievement automatically unlocked'
            )
            return {'msg': 'Achievement unlocked', 'image':"%s" % badge[0].image, 'code': messages.SUCCESS }
        except:
            return {'msg' : 'Achievement save error', 'image':"%s" % badge[0].image, 'code': messages.ERROR }
    else:
        return {'msg' : 'Already has this badge', 'image': '', 'code': messages.WARNING }

def classifyupdate(request,code):
    if (request.POST):
        resp = addvalidset(request,code)
        if resp:
            msg = {'update':False}
        else:
            msg = {'update': True}
    else:
        msg = {'update':False}
    #messages.warning(request,msg)
    return HttpResponse(json.dumps(msg),content_type='application/javascript')

def updatedataset(request,code):
    formdata = request.POST
    option = request.GET.get('mode','')
    if (formdata and option == 'display'):
        resp = updatedisplay(request,code)
        url = reverse('my-graph',args= [code])
        if resp:
            messages.warning(request,'Your preferences have not been saved.')
        else:
            messages.success(request,'Your display setting has been saved.')
    elif (formdata and option == 'valid'):
        resp = addvalidset(request,code)
        if resp:
            messages.warning(request,'None of your lightcurves have been saved.')
        else:
            messages.success(request,'Your selected classification has been saved.')
        url = reverse('average-graph',args= [code])
    else:
        messages.warning(request,'Nothing to save')
    return HttpResponseRedirect(url)



@login_required
def graphview(request,code,mode,calid):

    if mode == 'simple':
        return graphview_simple(request,code,mode,calid)
    elif mode == 'ave':
        return graphview_ave(request,code,mode,calid)
    elif mode == 'advanced':
        return graphview_advanced(request,code,mode,calid)

def graphview_simple(request,code,mode,calid):
# If graphview is simple

    # Stores the name of the observer from the request in variable o
    o = personcheck(request)

    # Stores the number of completed datasets with the total
    progress = checkprogress(o.user,code)

    # See first if statement
    n = 0

    # Creates a dataset object for the user
    d1 = ds.Dataset(code,o.user.username)

    # Returns information in 2 lists for the data being analysed as well as information on the datapoints
    data,points = d1.my_data()#my_data(o,code)

    # Returns list of data collections based on the exoplanet being analysed
    dc = DataCollection.objects.filter(person=o.user,planet=d1.planet)

    # If the number of data collections is greater than 0 (as defined earlier)
    if dc.count() > n:

        # Overrides n with an np.array in range 0 to the number of collections in dc
        n = range(0,dc.count())

        # Empty list
        cats = []

        # Goes through each entry in n and tries the following
        for order in n:
            try:
                ## Sometimes the sequence of calibrators is not continuous 0..n  -- BUG

                # Returns the name of the object being analysed
                dc0 = dc.filter(calid=order)[0]

                # Filter points to return one datapoint
                c = points.filter(pointtype='C',coorder=dc0)[:1]

                # Is this datapoint valid? Boolean
                valid = c[0].coorder.display

                # Create list of the name of the object, its order and whether it is valid
                coll = {'order' : order,
                        'name'  : c[0].coorder.source,
                        'valid' : valid,
                        }

                # Appends to the empty list cals
                cats.append(coll)

            # If cannot try, simply pass
            except:
                pass

    # If the count is less than n
    else:

        # Declare cats as being None (not an empty list)
        cats = None

    # Stores total number of analyses, those of which are completed and those of which have been classified has having a dip
    classif = classified(o,code)

    # Render the findings
    return render(request, 'agentex/graph_flot.html', {'event':d1.planet,
                                                            'data':data,
                                                            'n':n,
                                                            'sources':cats,
                                                            'classified':classif,
                                                            'progress' : progress,
                                                            'target':DataSource.objects.filter(event__name=code)[0].target})

@login_required
def graphview_ave(request,code,mode,calid):
    # If the mode is average rather than simple

    # Stores the name of the observer from the request in variable o
    o = personcheck(request)

    # Stores the number of completed datasets with the total
    progress = checkprogress(o.user,code)

    # See first if statement
    n = 0

    # Define empty list to store data
    data = []

    # get and restructure the average data JS can read it nicely
    # Stores the date and time at this instance
    now = datetime.now()

    # Calls photometry function and stores results

    cals,normcals,sb,bg,dates,stamps,ids,cats = photometry(code,o.user,progress)

    if not dates:
        messages.error(request,'Please analyse some images before moving on.')
        return HttpResponseRedirect(reverse('addvalue',args=[code]))


    # Determines the number of calibrator stars
    numcals = len(normcals)

    # Prints the normalised calibrators

    logger.error('The normalised calibrator stars are {}'.format(normcals))
    logger.error(dates)
    for i,id in enumerate(ids):
        #mycalibs = []

        # Empty lists to store both calibrators and normalised calibrators
        calibs = []
        normcalibs = []

        # Iterate over the number of normalised calibrators
        for j in range(0,numcals):

            # Appends calibs and normcalibs with the iterated members of cals
            calibs.append([cals[j][i],cats[j]['order']])
            #mycalibs.append(mycals[j][i])
            normcalibs.append(normcals[j][i])

        # Populates a list with id, datestamps etc
        line = {
                'id'        : id,
                'date'      : dates[i],
                'datestamp' : stamps[i],
                'data'      : { 'source' : sb[i],
                                'background' :  bg[i],
                                'calibration' :  normcalibs,
                                #'mycals'     :  mycalibs,
                                'calibrator' : calibs,
                            },
                }

        # Append data with line and break loop
        data.append(line)

    # Stores name of planet
    planet = Event.objects.filter(name=code)[0]

    ### Make sure person gets a different calibrator (that they haven't classified) after each POST

    # Set current calibrator to None
    currentcal = None

    # Returns the name of the source and the number of instances of it
    dec = Decision.objects.values('source__name').filter(person=o.user,planet__name=code,value__in=['D','N','B','P','R','S'],current=True).annotate(count=Count('source')).order_by('count')

    # Essentially this loop determines which calibrator is being analysed
    if calid:
        for cat in cats:
            # Which calibrator is being requested, if one is requested
            if int(cat['order']) == int(calid)-1:
                currentcal = {'order': cat['order'], 'sourcename' : "%s" % cat['sourcename'],'total':len(cats),'progress':dec.count()}
    else:
        if dec.count() == 0 and cats:
            currentcal = {'order': cats[0]['order'], 'sourcename' : "%s" % cats[0]['sourcename'], 'total':len(cats),'progress':dec.count()}
        elif dec.count() < len(cats):
            tmp, declist = zip(*dec.values_list('count','source__name'))
            for cat in cats:
                if (cat['sourcename']  not in declist):
                    currentcal = {'order': cat['order'], 'sourcename' : "%s" % cat['sourcename'], 'total':len(cats),'progress':dec.count()}
        elif dec:
            for cat in cats:
                if cat['sourcename'] == dec[0]['source__name']:
                    currentcal = {'order': cat['order'], 'sourcename' : "%s" % cat['sourcename'], 'total':len(cats),'progress':dec.count()}
    if currentcal:
        ## Send decision person made last time they were here
        mychoice = Decision.objects.values('value').filter(person=o.user,planet__name=code,value__in=['D','N','B','P','R'],source__name=currentcal['sourcename'])
        if mychoice:
            choice = mychoice.latest('taken')
            rev_dec = dict((v,k) for k, v in decisions.iteritems())
            prev = rev_dec[choice['value']]
        else:
            prev = None
        # How many have I classified
    elif len(cats) == 0 and calid == None:
        prev = None
    else:
        messages.error(request,'The lightcurve using the selected calibrator is not complete')
        return HttpResponseRedirect(reverse('average-graph',args=[planet.name]))
    #logger.debug(datetime.now() - now)
    classif = classified(o,code)
    resp = achievementscheck(o.user,planet,0,0,0,len(cats),0)
    unlock = False
    nunlock = 0
    msg = '<br />'

    for item in resp:
        if messages.SUCCESS == item['code'] :
            msg += "<img src=\""+settings.STATIC_URL+item['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />"
            unlock = True
            nunlock += 1

    if unlock :
        if nunlock > 1 : msg = 'Achievements unlocked'+msg
        else : msg = 'Achievement unlocked'+msg
        messages.add_message(request, messages.SUCCESS, msg)
    logger.debug('The classified objects (number selected to have a dip, total number of calibrator star data sets, number of those datasets are completed) {}'.format(classif))
    return render(request, 'agentex/graph_average.html', {'event': planet,
                                                            'data':data,
                                                            'sources':cats,
                                                            'cals':json.dumps(cats),
                                                            'calid': currentcal,
                                                            'prevchoice' : prev,
                                                            'classified':classif,
                                                            'progress' : progress,
                                                            'target':DataSource.objects.filter(event=planet)[0].target})

@login_required
def graphview_advanced(request,code,mode,calid):

    # Stores the name of the observer from the request in variable o
    o = personcheck(request)

    # Stores the number of completed datasets with the total
    progress = checkprogress(o.user,code)

    # Populate with data from the source, the cslibrator and the sky values
    opt = {'S' :'source','C':'calibrator','B':'sky'}

    # If dataid is in request.GET, extract the dataid
    if 'dataid' in request.GET:
        dataid = request.GET.get('dataid','')
    else:

        # Otherwise filter the datapoints to extract
        dataid = Datapoint.objects.filter(user=o[0].user).order_by('taken')[0].data.id

    # If still no luck, try lesser filter
    try:
        s = DataSource.objects.filter(id=dataid)[0]

    # If still not working, raise HTTP 404
    except:

        raise Http404

    # Filters the datapoints by reverse pointtype
    ps  = Datapoint.objects.filter(~Q(pointtype = 'R'),data = s).order_by('-pointtype')

    # Populates a list of the data
    datalist = [{'mine': ismypoint(o[0],dp.user),'x' : dp.xpos,'y' : dp.ypos, 'r' : dp.radius, 'value' : "%.0f" % dp.value,'type':opt[dp.pointtype]} for dp in ps]

    # Brings it all together
    line = {
            'id'        : "%i" % s.id,
            'date'      : s.timestamp.isoformat(" "),
            'datestamp' : timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,
            'data'      : datalist,
            }

    return render(request, 'agentex/graph_advanced.html', {'event':Event.objects.filter(name=code)[0],
                                                                    'framedata':line,
                                                                    'target':DataSource.objects.filter(event__name=code)[0].target,                                                                    'progress' : progress})
'''
def graphsuper(request,code):
    # Construct the supercalibrator lightcurve
    ds1 = ds.Dataset(planetid=code,userid=request.user.username)
    data = ds1.final()
    ###### Setting nodata to True and not showing each person their own data, but just for now
    return render(request, 'agentex/graph_super.html', {'event':ds1.planet,
                                                                'data':data,
                                                                'numsuper':13,
                                                                'target':ds1.target,
                                                                'nodata' : True})
'''

def datagen(code,user):

    # Extract name of exoplanet from the dataset
    event = Event.objects.get(name=code)

    # Collect sources
    sources = DataSource.objects.filter(event=event).order_by('timestamp')

    numsuper,fz,mycals,std,nodata = supercaldata(user,event)

    data = []

    for i,s in enumerate(sources):
        line = {
                'id'        : "%i" % s.id,
                'date'      : s.timestamp.isoformat(" "),
                'datestamp' : timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,
                'data'      : {
                                'mean' : fz[i],
                                'std'  : std[i],
                                'mine' : 'null',#myvals[i],
                    },
                }
        data.append(line)
    return data


def graphsuper(request,code):
    # Construct the supercalibrator lightcurve

    # Extract name of exoplanet from the dataset
    event = Event.objects.get(name=code)

    # Extract name of the target star from the dataset
    target = Target.objects.get(name=event.title[:-1])

    user = request.user

    # Call datagen to generate realtime data
    data = datagen(code,user)

    ###### Setting nodata to True and not showing each person their own data, but just for now
    return render(request, 'agentex/graph_super.html', {'event':event,
                                                                'data':data,
                                                                'numsuper':13,
                                                                'target':target,
                                                                'nodata' : True})

def infoview(request,code):
    ds = DataSource.objects.filter(event__name=code)[:1]

    if request.user.is_authenticated:
        person = personcheck(request)
        progress = checkprogress(person.user,code)
    else:
        progress = None
    try:
        data = ds[0]
    except:
        raise Http404
    #return render_to_response('agentex/info.html', {'object' : data, 'progress' : progress}, context_instance=RequestContext(request))
    return render(request, 'agentex/info.html', {'object' : data, 'progress' : progress})

def fitsanalyse(request):
    now = datetime.now()
    if (request.user.is_authenticated):
        person=request.user
    else:
        person = User.objects.filter(id=guestuser)[0]
    # Flag poor quality result
    #logger.debug(datetime.now() - now)
    flag = ''
    # Extract variables passed from the image
    # Order of variables sent is 'bg','source','cal1','cal2'...
    x = request.POST.get('x','').split(',')
    y = request.POST.get('y','').split(',')
    if (len(x) < 3 or len(y) < 3):
        response = {'message' : 'Please submit calibration, blank sky and source apertures.'}
        return HttpResponse(json.dumps(response),content_type='application/javascript')
    x = map(float,x)
    y = map(float,y)
    coords = zip(x,y)
    dataid = request.POST.get('dataid','')
    linex = list()
    liney = list()
    counts = list()

    ###########
    # Validate the input data
    # Check radius is less than a max size so the server does not have too much load
    # ***** No longer used as we fix radius from the outset ****
    #if r >= 70:
    #    response = {'message' : 'Apertures are too large. Please make your circles smaller'}
    #    return HttpResponse(json.dumps(response),content_type='application/javascript')
    # Check all apertures are away from frame edge
    d = DataSource.objects.filter(id=int(dataid))[:1]
    r = d[0].event.radius
    for co in coords:
        xi = co[0]
        yi = co[1]
        if (xi-r < 0 or xi+r >= d[0].max_x or yi-r < 0 or yi+r > d[0].max_y ):
            response = {'message' : 'Please make sure your circles are fully within the image'}
            return HttpResponse(json.dumps(response),content_type='application/javascript')

    #logger.debug(datetime.now() - now)
    # Grab a fits file
    dfile = "%s%s" % (settings.DATA_LOCATION,d[0].fits)
    #logger.debug(dfile)
    dc = fits.getdata(dfile,header=False)
    #logger.debug(datetime.now() - now)

    # Find all the pixels a radial distance r from x0,y0
    for co in coords:
        x0 = int(floor(co[0]))
        y0 = int(floor(co[1]))
        # Sum for this aperture
        sum = 0
        numpix = 0
        ys = y = y0 -r
        ye = y0 +r
        vline = list()
        hline = list()
        while (y < ye):
            angle = np.fabs(1.*(y-y0)/r)
            dx = int(np.sin(np.arccos(angle))*r)
            x = xs = x0 - dx
            xe = x0 + dx
            while (x < xe):
                sum += float(dc[y][x])
                x += 1
                if (x == x0):
                    hline.append(float(dc[y][x]))
                if (y == y0):
                    vline.append(float(dc[y][x]))
                    logger.debug("x = %s, y= %s val=%s" % (x,y,float(dc[y][x])))
                numpix += 1
            y += 1
        linex.append(hline)
        liney.append(vline)
        counts.append(sum)
    #logger.debug(datetime.now() - now)

    # Send back the raw total counts. Analysis can be done when the graph is produced.
    pointsum = {'bg' :  '%.2f' % counts[0], 'sc' : '%.2f' % counts[1], 'cal' : counts[2:]}
    lines = {'data' : {
               'coords' : {'xy' : coords,'r':r},
                'sum'   : pointsum,
                'points' : {'bg':
                                {'horiz' : linex[0],
                                'vert' : liney[0],
                                },
                            'sc':
                                {'horiz' : linex[1],
                                'vert' : liney[1],
                                },
                            'cal':
                                {'horiz' : linex[2:],
                                'vert' : liney[2:],
                                },
                            },
                #'quality' : flag,
               'pixelcount' : numpix,
                },
            }
    #logger.debug((datetime.now() - now))
    # save measurement data on the backend automatically
    entrymode = request.POST.get('entrymode','M')
    resp = savemeasurement(person,pointsum,coords,dataid,entrymode)
    if  resp['code'] == messages.ERROR:
        lines = {'error':  resp['msg']}
    else:
        messages.add_message(request, resp['code'], resp['msg'])
    return HttpResponse(json.dumps(lines,indent = 2))

def measurementsummary(request,code,format):
    ####################
    # Return a measument data set based on event code and having either 'json' or 'xml' format
    data = []
    maxpixel = 1024
    csv =""
    if (request.user.is_authenticated):
        o = request.user
    else:
        o = guestuser
    options = request.GET.get('mode','')
    if (format == 'xhr' and options ==''):
        #cals = []
        sources = []
        dates = []
        stamps = []
        rawcals = []
        timestamps = []
        cals = []
        mypoints = Datapoint.objects.filter(user=o[0].user,data__event__name=code).order_by('data__timestamp')
        for d in mypoints.filter(pointtype='S'):
            dates.append(d.data.timestamp.isoformat(" "))
            stamps.append(timegm(d.data.timestamp.timetuple())+1e-6*d.data.timestamp.microsecond)
            timestamps.append(d.data.timestamp)
        sources = np.array(mypoints.filter(pointtype='S').values_list('value',flat=True))
        ids = mypoints.filter(pointtype='S').values_list('data__id',flat=True)
        bg = np.array(mypoints.filter(pointtype='B').values_list('value',flat=True))
        sb = sources -bg
        cs = mypoints.filter(pointtype='C').order_by('coorder__calid')
        maxcals = cs.aggregate(Max('coorder__calid'))['coorder__calid__max']
        if maxcals == None:
            maxcals = -1
        for i in range(0,maxcals+1):
            vals = []
            for d,item in enumerate(ids):
                cp = cs.filter(data__timestamp=timestamps[d])
                if len(cp) > i:
                    vals.append(sb[d]/(cp[i].value-bg[d]))
                else:
                    vals.append(0.0)
            maxvals = r_[vals[:3],vals[-3:]]
            nz = maxvals.nonzero()
            maxval = mean(maxvals[nz])
            cals.append(list(vals/maxval))
        datapoints = {'calibration' : cals, 'source' : list(sources),'background':list(bg),'dates':dates,'id':list(ids),'datestamps':stamps,'n':maxcals+1}
        dataid = request.GET.get('dataid','')
        return HttpResponse(json.dumps(datapoints,indent=2),content_type='application/javascript')
    elif (format == 'xhr' and options=='ave'):
        #cals = []
        #cs = mypoints.filter(pointtype='C').order_by('coorder__calid')
        maxcals = DataCollection.objects.filter(person=o[0].user,planet__name=code).aggregate(Max('calid'))['calid__max']
        if maxcals:
            # cals,normcals,mycals,sb,bg,dates,stamps,ids,cats = myaverages(code, o[0].user)
            cals,normcals,sb,bg,dates,stamps,ids,cats = averagecals(code, o[0].user)
            # datapoints = {'calibration' : normcals, 'mycals': mycals,'source' : sb,'background':bg,'calibrator':cals,'dates':dates,'id':ids,'datestamps':stamps,'n':maxcals+1}
            datapoints = {'calibration' : normcals, 'source' : sb,'background':bg,'calibrator':cals,'dates':dates,'id':ids,'datestamps':stamps,'n':maxcals+1}
        else:
            datapoints = {'calibration':None}
        return HttpResponse(json.dumps(datapoints,indent=2),content_type='application/javascript')
    elif (format == 'xhr' and options == 'super'):
        # Construct the supercalibrator lightcurve
        planet = Event.objects.filter(name=code)[0]
        numsuper, normvals, std,radiusratio = supercaldata(user,planet)
        sources = DataSource.objects.filter(event=planet).order_by('timestamp')
        dates = []
        for s in sources:
            dates.append(timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,)
        datapoints = {'normalised' : normvals, 'dates':dates, 'std':std}
        return HttpResponse(json.dumps(datapoints),content_type='application/javascript')
    elif (request.GET and format == 'json'):
        dataid = request.GET.get('dataid','')
        s = DataSource.objects.filter(id=dataid)[0]
        ps  = Datapoint.objects.filter(~Q(pointtype = 'R'),data = s).order_by('-pointtype')
        datalist = [{'mine': ismypoint(o[0],dp.user),'x' : dp.xpos,'y' : dp.ypos, 'r' : dp.radius, 'value' : dp.value,'type':dp.pointtype} for dp in ps]
        line = {
                'id'        : "%i" % s.id,
                'date'      : s.timestamp.isoformat(" "),
                'datestamp' : timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,
                'data'      : datalist,
                }
        return HttpResponse(json.dumps(line,indent = 2),content_type='application/javascript')
    else:
        planet = Event.objects.filter(name=code)[0]
        numsuper, normvals, myvals, std,radiusratio = supercaldata(request.user,planet)
        sources = DataSource.objects.filter(event=planet).order_by('timestamp')
        n = 0
        if format == 'json':
            data = []
            if len(normvals) == planet.numobs :
                for i,s in enumerate(sources):
                    line = {
                            'id'        : "%i" % s.id,
                            'date'      : s.timestamp.isoformat(" "),
                            'datestamp' : timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,
                            'data'      : {
                                            'mean' : normvals[i],
                                            'std'  : std[i],
                                            'mine' : myvals[i],
                                },
                            }
                    data.append(line)
            else:
                data = None
            return HttpResponse(json.dumps(data,indent = 2),content_type='application/javascript')
        # elif format == 'xml':
        #     return render_to_response('agentex/data_summary.xml',{'data':data},content_type="application/xhtml+xml")
        elif format == 'csv':
            csv = "# Date of observation, Unix timestamp, normalised average values, standard deviation, my normalised values\n"
            for i,s in enumerate(sources):
                csv += "%s, %s, %s, %s, %s\n" % (s.timestamp.isoformat(" "),timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,normvals[i],std[i],myvals[i])
            return HttpResponse(csv,content_type='text/csv')

def calibratemydata(code,user):
    #cs = Datapoints.objects.filter(pointtype='C',user=user).order_by('coorder__calid')
    ds = DataSource.objects.filter(event__name=code).order_by('timestamp')
    stars = DataCollection.objects.filter(planet__name = code,person=user).values_list('source',flat=True)
    cals = []
    # mycals = []
    # dates = []
    # stamps = []
    # timestamps = []
    # ids = []
    # scA = []
    # bgA = []
    for i,st in enumerate(stars):
        vals = []
        #myvals = []
        for d in ds:
            points = Datapoint.objects.filter(data=d)
            cp = points.filter(pointtype='C',coorder__source=st).aggregate(ave=Avg('value'))['ave']
            sb = points.filter(pointtype='S').aggregate(ave=Avg('value'))['ave']
            bg = points.filter(pointtype='B').aggregate(ave=Avg('value'))['ave']
            if cp:
                vals.append((sb-bg)/(cp-bg))
            else:
                vals.append(0.0)
            mypoint = points.filter(user=user)
            if mypoint:
                vals.append((sb-bg)/(mypoint[0].value-bg))
            else:
                vals.append('0.0')
        maxval = max(vals)
        #nz = maxvals.nonzero()
        #maxval = mean(maxvals)
        cals.append(list(vals/maxval))
        #mycals.append(list(myvals/maxval))
    return mycals

'''
def myaverages(code,person):
    return c_myaverages(code,person)
'''

def myaverages(code,person):
    ds = DataSource.objects.filter(event__name=code).order_by('timestamp').values_list('id',flat=True)
    valid_user = False
    if person:
        if person.is_authenticated:
            valid_user = True
    if valid_user:
        now = datetime.now()
        cals = []
        mycals = []
        dates = []
        stamps = []
        timestamps = []
        normcals = []
        maxvals = []
        cats = []
        # Find which Cat Sources I have observed and there is a complete set of (including other people's data)
        # Unlike CalibrateMyData it only includes set where there are full sets
        e = Event.objects.filter(name=code)[0]
        dc = DataCollection.objects.filter(~Q(source=None),person=person,planet=e).order_by('calid')
        cs = CatSource.objects.filter(id__in=[c.source.id for c in dc]).annotate(count=Count('datacollection__datapoint')).filter(count__gte=e.numobs).values_list('id',flat=True)
        mydecisions = Decision.objects.filter(person=person,current=True,planet=e,value='D').values_list('source__id',flat=True)
        if cs.count() > 0:
            # Only use ones where we have more than numobs
            for c in dc:
                # make sure these are in the mydecision list (i.e. I've said they have a Dip)
                if c.source.id in mydecisions:
                    v = Datapoint.objects.filter(coorder__source=c.source.id,pointtype='C',user=person).order_by('data__timestamp').values_list('data__id','value')
                    cals.append(dict(v))
            if cals:
                # Only proceed if we have calibrators in the list (i.e. np.arrays of numobs)
                points = Datapoint.objects.filter(user=person,data__event__name=code).order_by('data__timestamp')
                scA = points.filter(pointtype='S').values_list('data__id','value')
                bgA = points.filter(pointtype='B').values_list('data__id','value')
                # Create a list of normalised values with gaps if I haven't done the full dataset but have contributed to a 'Dip' classification
                sc=dict(scA)
                bg=dict(bgA)
                sc = dictconv(sc,ds)
                sc = np.array(sc)
                bg = dictconv(bg,ds)
                bg = np.array(bg)
                for cal in cals:
                    val = (sc - bg)/(np.array(dictconv(cal,ds))-bg)
                    val = np.nan_to_num(val)
                    normcals.append(val)
                normmean = mean(normcals,axis=0)
                return list(normmean/max(normmean))
    # If they have no 'D' decisions
    return [0.]*ds.count()

def admin_averagecals(code,person):
    # Uses and SQL statement to try to speed up the query for averaging data points
    # If person == 0 this will return all calibrator values individually - for problem solving
    now = datetime.now()
    cals = []
    mycals = []
    dates = []
    stamps = []
    timestamps = []
    normcals = []
    maxvals = []
    callist = []
    cats = []
    # Find which Cat Sources I have observed and there is a complete set of (including other people's data)
    # Unlike CalibrateMyData it only includes set where there are full sets
    e = Event.objects.filter(name=code)[0]
    if person == 0:
        dc = DataCollection.objects.filter(~Q(source=None),planet__name=code).values_list('source__id',flat=True).distinct()
        cs = CatSource.objects.filter(id__in=[c for c in dc]).annotate(count=Count('datacollection__datapoint')).filter(count__gte=e.numobs).values_list('id',flat=True).distinct()
        dcall = DataCollection.objects.filter(planet=e,source__in=cs).values_list('id',flat=True)
        logger.debug("** Collections %s" % dcall.count())
        if cs.count() > 0:
            # Only use ones where we have more than numobs
            for c in dc:
                # make sure these are in the CatSource list (can't use cs because the order isn't right)
                if c in cs:
                    people = Decision.objects.filter(source__id=c,current=True,value='D').values_list('person',flat=True)
                    if people:
                        v = Datapoint.objects.filter(coorder__source=c,pointtype='C',user__id__in=people).order_by('data__timestamp').values_list('data__id').annotate(Avg('value'))
                    else:
                        v = Datapoint.objects.filter(coorder__source=c,pointtype='C').order_by('data__timestamp').values_list('data__id').annotate(Avg('value'))
                    # Double check we have same number of obs and cals
                    if v.count() == e.numobs:
                        ids,b = zip(*v)
                        cals.append(list(b))
                        decvalue_full = Decision.objects.filter(source=c,planet__name=code,current=True).values_list('value').annotate(total=Count('id'))
                        decvalue = dict((str(key),value) for key,value in decvalue_full)
                        source = CatSource.objects.get(id=c)
                        cat_item = {'sourcename':str(source.name),'catalogue':str(source.catalogue),'sourceid': str(c),'include':source.final}
                        cat_item['decisions'] = decvalue
                        cats.append(cat_item)
                        callist.append(c)
    else:
        dc = DataCollection.objects.filter(~Q(source=None),person=person,planet__name=code).order_by('calid')
        cs = CatSource.objects.filter(id__in=[c.source.id for c in dc]).annotate(count=Count('datacollection__datapoint')).filter(count__gte=e.numobs).values_list('id',flat=True).distinct()
        dcall = DataCollection.objects.filter(planet=e,source__in=cs).values_list('id',flat=True)
        logger.debug("** Collections %s" % dcall.count())
        if cs.count() > 0:
            # Only use ones where we have more than numobs
            for c in dc:
                # make sure these are in the CatSource list (can't use cs because the order isn't right)
                if c.source.id in cs:
                    v = Datapoint.objects.filter(coorder__source=c.source.id,pointtype='C').order_by('data__timestamp').values_list('data__id').annotate(Avg('value'))
                    # Double check we have same number of obs and cals
                    if v.count() == e.numobs:
                        ids,b = zip(*v)
                        cals.append(list(b))
                        try:
                            decvalue = Decision.objects.filter(source=c.source,person=person,planet__name=code,current=True)[0].value
                        except:
                            decvalue ='X'
                        cat_item = {'sourcename':c.source.name,'catalogue':c.source.catalogue}
                        cat_item['decsion'] = decvalue
                        cat_item['order'] = str(c.calid)
                        cats.append(cat_item)
                        callist.append(c.source.id)
    if callist:
        # Only proceed if we have calibrators in the list (i.e. np.arrays of numobs)
        ds = DataSource.objects.filter(event=e).order_by('timestamp')
        users = DataCollection.objects.filter(id__in=dcall).values_list('person',flat=True).distinct()
        maxnum = ds.count()
        dsmax1 = ds.aggregate(Max('id'))
        dsmax = dsmax1['id__max']
        dsmin = dsmax - maxnum
        ds = ds.values_list('id',flat=True)
        if person == 0:
            people = Decision.objects.filter(planet=e,value='D',current=True).values_list('person',flat=True).distinct()
            dp = Datapoint.objects.filter(data__event=e,user__id__in=people)
            sc = []
            bg = []
            for d in ds:
                sc_ave = dp.filter(pointtype='S',data__id=d).aggregate(val=Avg('value'))
                bg_ave = dp.filter(pointtype='B',data__id=d).aggregate(val=Avg('value'))
                sc.append(sc_ave['val'])
                bg.append(bg_ave['val'])
        else:
            sc_my = ds.filter(datapoint__pointtype='S',datapoint__user=person).annotate(value=Sum('datapoint__value')).values_list('id','value')
            bg_my = ds.filter(datapoint__pointtype='B',datapoint__user=person).annotate(value=Sum('datapoint__value')).values_list('id','value')
            if sc_my.count() < maxnum:
                return cals,normcals,[],[],dates,stamps,[],cats
            else:
                tmp,sc=zip(*sc_my)
                tmp,bg=zip(*bg_my)
        # Convert to numpy np.arrays to allow simple calibrations
        sc = np.array(sc)
        bg = np.array(bg)
        for cal in cals:
            val = (sc - bg)/(np.array(cal)-bg)
            maxval = mean(r_[val[:3],val[-3:]])
            maxvals.append(maxval)
            norm = val/maxval
            normcals.append(list(norm))
        # Find my data and create unix timestamps
        unixt = lambda x: timegm(x.timetuple())+1e-6*x.microsecond
        iso = lambda x: x.isoformat(" ")
        times = ds.values_list('timestamp',flat=True)
        stamps = map(unixt,times)
        dates = map(iso,times)
        if person == 0:
            return normcals,stamps,[int(i) for i in ids],cats
        return cals,normcals,list(sc),list(bg),dates,stamps,[int(i) for i in ids],cats
    if person == 0:
        return normcals,stamps,[],[]
    return cals,normcals,[],[],dates,stamps,[],cats

def averagecals_async(e):
    #e = Event.objects.get(name=code)
    catsource = DataCollection.objects.values_list('source').filter(planet=e, display=True).annotate(Count('source'))
    for cat in catsource:
        if cat[0] != None:
            dps = Datapoint.objects.filter(data__event=e, coorder__source__id=cat[0], pointtype='C').order_by('data__timestamp').values_list('data').annotate(Avg('value'))
            # Double check we have same number of obs and cals
            if dps.count() == e.numobs:
                ids,values = zip(*dps)
                a = AverageSet.objects.get_or_create(star=CatSource.objects.get(id=cat[0]),planet=e,settype='C')
                a[0].values = ";".join([str(i) for i in values])
                a[0].save()
                logger.debug("Updated average sets on planet %s for %s" % (e.title,CatSource.objects.get(id=cat[0])))
    # Make averages for Source star and Background
    for category in ['S','B']:
        dps = Datapoint.objects.filter(data__event=e, pointtype=category).order_by('data__timestamp').values_list('data').annotate(Avg('value'))
        # Double check we have same number of obs and cals
        if dps.count() == e.numobs:
            ids,values = zip(*dps)
            a = AverageSet.objects.get_or_create(planet=e,settype=category)
            a[0].values = ";".join([str(i) for i in values])
            a[0].save()
            logger.debug("Updated average sets on planet %s for %s" % (e.title,category))
    return

def calstats(user,planet,decs):

    # Create empty list to store calibrators and datapoints
    calibs = []
    mypoints = []

    # Count number of decisions
    numsuper = decs.count()

    # Lists are created here
    peoplelst,sourcelst,tmp = zip(*decs)

    # Organise list of people and sources
    people = set(peoplelst)
    sources = set(sourcelst)

    # Import entire Datapoint database and sort by timestamp
    cache_name = '{}_datapoints'.format(planet)
    db = cache.get(cache_name)
    if not db:
        db = Datapoint.objects.filter(ident=planet).values_list('user_id','coorder__source','value','pointtype').order_by('tstamp')
        cache.set(cache_name, db, 120)

    # Convert to numpy np.array
    dp_array = np.array(db)

    # Read in all values of calibrators
    calvals_data = Datapoint.objects.values_list('user_id','coorder__source','value').filter(coorder__source__in=sources,pointtype='C',coorder__source__final=True,coorder__complete=True,coorder__display=True).order_by('tstamp')

    # Convert to numpy np.array
    calvals_array = np.array(vstack(calvals_data))

    # Iterate over each person
    for p in people:

        # Empty list to store calibrators
        calslist = []


        # Query datapoints to extract all values for given planet
        # Both dp_array[:,1] and calvals_array[:,0] extract entries for user_id==p from column 0
        vals = dp_array[dp_array[:,0]==p]
        if vals.size == 0:
            # Jump to the next person if we don't have any values
            continue

        calvals = calvals_array[calvals_array[:,0]==p]
        if calvals.size == 0:
            # Jump to the next person if we don't have any calibrator values
            continue

        # Query vals to extract average values

        # vals[:,6]=='S' and vals[:,6]=='B' extract the entries from vals that have pointtype=='S' and 'B' in column 6. sc_extract[:,4] and bg_extract[:,4] pulls the exact source and background values for those entries from column 4
        sc_extract = vals[vals[:,3]=='S']
        sc = sc_extract[:,2]

        bg_extract = vals[vals[:,3]=='B']
        bg = bg_extract[:,2]
        # Iterates over the number of sources defined earlier
        for c in sources:

            # Determines their associated averages
            # Performs similar routine to above to extract the source type from column 2, and then the values from column 3
            calpoints_extract = calvals[calvals[:,1]==c]
            calpoints = calpoints_extract[:,2]

            # If there are more calibrator points than observations
            if len(calpoints) == planet.numobs:
                # Append calpoints
                calslist.append(list(calpoints))

        # Loops through calslist
        if len(calslist) > 0:
            # if settings.LOCAL_DEVELOPMENT: logger.debug("\033[94mWe have calibrators\033[1;m")

            # Stacks the values
            calstack = np.array([])
            calstack = vstack(calslist)
            #logger.debug('calstack=',calstack)

            # This throws a wobbly sometimes
            cc = (sc-bg)/(calstack-bg)
            calibs.append(cc.tolist())

        else:
            if settings.LOCAL_DEVELOPMENT:
                pass
                #logger.debug("\033[1;35mThere are no calibrators in the list!!\033[1;m")
        #logger.debug("%s %s - %s" % (ti, p, datetime.now()-now))
        #ti += 1

    # Create normalisation function
    norm_a = lambda a: mean(r_[a[:3],a[-3:]])
    mycals = []

    #logger.debug('calibs=', calibs)

    try:
        # Stacks all of the calibrators
        cala = vstack(calibs)
        #logger.debug('cala=', cala)

        # Normalises stacked calibrators
        norms = apply_along_axis(norm_a, 1, cala)
        #logger.debug('norms=', norms)

        # Determines the length of the stacked calibrators
        dim = len(cala)
        #logger.debug('dim=', dim)

        # Normalises the calibrators
        norm1 = cala/norms.reshape(dim,1)
        #logger.debug('norms.reshape(dim,1)=', norms.reshape(dim,1))
        #logger.debug('norm1=', norm1)

        # Empty list to store calibrators
        mynorm1=[]

        # If mypoints is not an empty list
        if mypoints != []:
            #mynorms = apply_along_axis(norm_a, 1, mypoints)
            # Averages the datapoints
            myaves = average(mypoints,0)
            # Averages the normalised points
            mynorm_val = norm_a(myaves)

            # Normalises the averages
            mycals = list(myaves/mynorm_val)
    except Exception as e:
        logger.error(e)
        logger.error("\033[1;35mHave you started again but not removed all the data?\033[1;m")
        return None,[],[],[],None
    #if dim != len(mycals):
    # check if I have a full set of data, if not we need to do all the calibrator averages manually
    # Performs mean statistics (normalise, variance, standard dev.)
    norm_alt = mean(norm1,axis=0)
    variance = var(norm1,axis=0)
    std = np.sqrt(variance)
    fz = list(norm_alt)

    # Final return statements
    nodata = False
    if mycals == []:
        mycals = myaverages(planet,user)
        nodata = True
        return numsuper,fz,mycals,list(std),nodata
    else:
        return None,[],[],[],None


def supercaldata(user,planet):

    # The commented out elements within this function are the original function. It
    # (and calstats) were originally one function. To restore functionality, simply
    # delete calstats and uncomment the code embraced in ''' here (and remove the
    # return statement at the bottom of the page).

    '''
    # Create empty list to store calibrators and datapoints
    calibs = []
    mypoints = []
    #ti = 0.
    '''

    # assume data which has Decisions forms part of a complete set
    # People and their sources who have Dips in the select planet

    # Store the date and time at the instant of the function call
    #now = datetime.now()

    # Extract the name of the planet being analysed
    planet = Event.objects.get(name=planet)

    # Pull all of the decisions into an object
    decs = Decision.objects.values_list('person','source').filter(value='D', current=True, planet=planet, source__datacollection__display=True).annotate(Count('source'))
    if decs:
        return calstats(user,planet,decs)


def leastmeasured(code):
    coords = []
    e = Event.objects.filter(name=code)[:1]
    dc = DataCollection.objects.values('source').filter(~Q(source=None),planet__name=code).annotate(count = Count('source')).order_by('count')[:4]
    for coll in dc:
        s = CatSource.objects.get(id=coll['source'])
        coords.append({'x':int(s.xpos),'y':int(s.ypos),'r':int(e[0].radius)})
    return coords


def update_web_pref(request,setting):
    #################
    # AJAX update user preference for web or  manual input of data
    if (request.user.is_authenticated):
        person = request.user
    else:
        person = guestuser
    o = person
    if setting == 'yes':
        o.update(dataexplorview=True)
        return HttpResponse("Setting changed to use web view")
    elif setting == 'no':
        o.update(dataexploreview = False)
        return HttpResponse("Setting changed to use manual view")
    else:
        return HttpResponse("Setting unchanged")

def average_sources(code):
    typep = ('S','C','B')
    ds = DataSource.objects.filter(name=code)
    for s in ds:
        points = Datapoint.objects.filter(data=s)
        dates = points.values_list('taken',flat=True)
        for date in dates:
            entry = points.objects.filter(taken=date)

def calibrate_update(code):
    dates = Datapoint.objects.values_list('taken',flat=True).filter(data__event__name=code).annotate(Count('taken'))
    for date in dates:
        measurement = Datapoint.objects.filter(taken=date,data__event__name=code)
        source = measurement.filter(pointtype='S')
        calib = measurement.filter(pointtype='C')
        backg = measurement.filter(pointtype='B')
        value = (source[0].value - backg[0].value)/(calib[0].value - backg[0].value)
        reduced = measurement.filter(pointtype='R')[0]
        reduced.value = value
        reduced.save()
        logger.debug("Reduced %s" % date)
def calibrate(measurement):
    source = measurement.filter(pointtype='S')
    calib = measurement.filter(pointtype='C')
    backg = measurement.filter(pointtype='B')
    value = (source[0].value - backg[0].value)/(calib[0].value - backg[0].value)
    return value
def img_coord_conv(x,size):
    newx = []
    entries = x.split(",")
    for entry in entries:
        newx.append(floor(float(entry)*size))
    return newx
def ismypoint(person,datauser):
    if person.user == datauser:
        return True
    else:
        return False

def classified(o,code):
    dcs = Decision.objects.values('source').filter(person=o.user,planet__name=code).annotate(last = Max('taken'))
    dips = Decision.objects.filter(taken__in=[d['last'] for d in dcs],person=o.user,planet__name=code,value='D').count()
    classifications = Decision.objects.values('source').filter(person=o.user,planet__name=code).annotate(Count('value')).count()
    totalcalibs = DataCollection.objects.values('source').filter(person=o.user,planet__name=code).annotate(Count('display')).count()
    return {'total' : totalcalibs, 'done':classifications,'dip':dips}
def checkprogress(person,code):
    n_analysed = Datapoint.objects.filter(user=person, data__event__name=code,pointtype='S').count()
    n_sources = DataSource.objects.filter(event__name=code).count()
    if (n_sources == 0):
	    progress = {'percent'   : "0.0",
                'done'      : n_analysed,
                'total'     : n_sources,}
    else:
	    progress = {'percent'   : "%.0f" % (float(n_analysed)*100/float(n_sources)),
                'done'      : n_analysed,
                'total'     : n_sources,}
    return progress


def fetch_averages_sql(dsmin,dsmax,pointtype,users):
    cursor = connection.cursor()
    users_str = [int(i) for i in users]
    params = [pointtype,dsmin,dsmax,users_str]
    cursor.execute('SELECT dp.data_id, avg(dp.value) FROM dataexplorer_datapoint as dp RIGHT JOIN dataexplorer_datasource AS ds on dp.data_id = ds.id WHERE dp.pointtype = %s AND (dp.data_id BETWEEN %s AND %s) AND dp.user_id IN %s GROUP BY dp.data_id order by ds.timestamp', params)
    result = list(cursor.fetchall())
    #ave_values = dict(result)
    return result
def dictconv(data,ref):
    tmp = []
    for i in ref:
        try:
            tmp.append(data[i])
        except:
            tmp.append(0.)
    return tmp

def update_final_display():
    c = CatSource.objects.all()
    c.update(final=True)
    decs = Decision.objects.filter(value='D',current=True)
    for d in decs:
        dc = DataCollection.objects.filter(person=d.person,source=d.source)
        dc.update(display=True)

def update_cat_sources(username,planetcode):
    event = Event.objects.get(name=planetcode)
    points = Datapoint.objects.filter(user__username=username,data__id=event.finder,pointtype='C')
    for p in points:
        cats = CatSource.objects.filter(xpos__lt=p.xpos+5,ypos__lt=p.ypos+5,xpos__gt=p.xpos-5,ypos__gt=p.ypos-5,data__event=event)
        dc = p.coorder
        if cats:
            dc.source=cats[0]
        else:
            dc.source=None
        dc.save()
