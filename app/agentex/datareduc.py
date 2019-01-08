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

All non render/page based views are stored here, rather than views.py.
'''
from astropy.io import fits
from calendar import timegm
from datetime import datetime,timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.serializers import serialize
from django.db import connection
from django.db.models import Count, Avg, Min, Max, Variance, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.urls import reverse
from itertools import chain
from rest_framework import status
from rest_framework.response import Response
from time import mktime
import numpy as np

from agentex.models import *
from agentex.forms import DataEntryForm, RegisterForm, CommentForm,RegistrationEditForm
import agentex.dataset as ds
from agentex.utils import achievementscheck

from agentex.agentex_settings import planet_level
from agentex.utils import dictconv

import logging

logger = logging.getLogger(__name__)

def personcheck(request):
    return request.user

def calibrator_data(calid,code):
    data = []
    sources, times = zip(*DataSource.objects.filter(event__slug=code).values_list('id','timestamp').order_by('timestamp'))
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
        #print(sc_norm,bg_norm,c_norm)
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
            ave = np.array(ave_measurement[0].data)
            mine = zip(*measurements.values_list('data','value'))
            try:
                my_ids = [ids.index(x) for x in mine[0]]
                ave[my_ids] = mine[1]
            except Exception as e:
                print(e)
            return ave
        else:
            return np.array([])
    elif progress['done'] == progress['total']:
        mine = np.array(measurements.values_list('value',flat=True))
        return mine
    elif not progress:
        print("No progress was passed")
        return np.array([])
    else:
        print("Error - too many measurements: %s %s" % (measurements.count() , numobs))
        return np.array([])

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
        sc = np.array(averages.filter(star=None,settype='S')[0].data)
        bg = np.array(averages.filter(star=None,settype='B')[0].data)
    # Make a combined list of all calibration stars used by 'person'
    for calibrator in dc:
        if person:
            measurements = dps.filter(pointtype='C',coorder=calibrator)
            ave = average_combine(measurements,averages,ids,calibrator.source,'C',progress)
        else:
            ave_cal = averages.filter(star=calibrator,settype='C')
            if ave_cal.count() > 0:
                ave = np.array(ave_cal[0].data)
            else:
                ave = np.array([])
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
    dates = []
    stamps = []

    # Call in averages
    cals,sc,bg,times,ids,cats = calibrator_averages(code,person,progress)

    indexes = [int(i) for i in ids]
    #sc = np.array(sc)
    #bg = np.array(bg)

    # Iterate over every calibrator
    for cal in cals:
        if len(cal) == progress['total']:
            #### Do not attempt to do the photmetry where the number of calibrators does not match the total
                # Determine calibrated flux from source
                val = (sc - bg)/(cal-bg)
                # Determine maximum flux from source
                maxval = np.mean(np.r_[val[:3],val[-3:]])
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



def measure_offset(d,person,basiccoord):
    # Find the likely offset of this new calibrator compared to the basic ones and find any sources within 5 pixel radius search
    finderid = d.event.finder
    finderdp = Datapoint.objects.values_list('xpos','ypos').filter(user=person,data__id=finderid,pointtype='C',coorder__calid__lt=3).order_by('coorder__calid')
    finder = basiccoord - np.array(finderdp)
    t = np.transpose(finder)
    xmean = np.mean(t[0])
    ymean = np.mean(t[1])
    return xmean,ymean

def updatedisplay(request,code):
    # Wipe all the validations for user and event
    o = personcheck(request)
    dc = DataCollection.objects.filter(person=o.user,planet=Event.objects.get(name=code),complete=True)
    dc.update(display = False)
    empty = True
    formdata = request.POST
    for i,val in formdata.items():
        if i[4:] == val:
            # Add validations back one by one
            col = dc.filter(calid=val)
            col.update(display= True)
            empty = False
    return empty

def addvalidset(request,code):
    o = personcheck(request)
    calid = request.POST.get('calid','')
    choice1 = request.POST.get('choice1','')
    choice2 = request.POST.get('choice2','')
    point = DataCollection.objects.filter(person=o.user,calid=calid,planet__name=code)
    planet = Event.objects.filter(name=code)[0]
    if choice1 and point and calid:
        value = decisions[choice1]
        source = point[0].source
        old = Decision.objects.filter(person=o.user,planet=planet,source=source)
        old.delete()
        decision1 = Decision(source=source,
                        value=value,
                        person=o.user,
                        planet=planet)

        if choice2:
            value2 = decisions[choice2]
            decision2 = Decision(source=source,
                            value=value2,
                            person=o.user,
                            planet=planet,
                            current=True)
            decision2.save()
        else:
            decision1.current = True
        decision1.save()
        return False
    else:
        return True

@login_required
def my_data(o,code):
    data = []
    sources = DataSource.objects.filter(event__slug=code).order_by('timestamp')
    points  = Datapoint.objects.filter(data__event__slug=code,user=o.user)
    for s in sources:
        ps = points.filter(data=s)
        myp = ps.filter(pointtype='S')
        try:
            mypoint = '%f' % myp[0].value
        except:
            mypoint = 'null'
        cals = ps.filter(pointtype='C').values_list('value',flat=True).order_by('coorder')
        line = {
                'id'        : "%i" % s.id,
                'date'      : s.timestamp.isoformat(" "),
                'datestamp' : timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,
                'data'      : { 'source' : list(ps.filter(pointtype='S').values_list('value',flat=True)),
                                'background' :  list(ps.filter(pointtype='B').values_list('value',flat=True)),
                                'calibrator' :  list(cals),
                            },
                }
        data.append(line)
    return data,points

def fitsanalyse(data):
    coords = list(zip(data['x'], data['y']))
    datasource = DataSource.objects.get(pk=data['id'])
    # Grab a fits file
    dfile = "%s%s" % (settings.DATA_LOCATION,datasource.fits)
    #logger.debug(dfile)
    dc = fits.getdata(dfile,header=False)
    r = datasource.event.radius
    linex = list()
    liney = list()
    counts = list()

    # Find all the pixels a radial distance r from x0,y0
    for co in coords:
        x0 = int(np.floor(co[0]))
        y0 = int(np.floor(co[1]))
        # Sum for this aperture
        sum = 0
        numpix = 0
        ys = y = y0 - r
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

    return lines

def savemeasurement(person, lines, dataid, mode):
    pointsum = lines['data']['sum']
    coordsxy = lines['data']['coords']
    # Only update the user's preference if they change it
    pointtype = {'sc':'S','bg':'B'}
    coords = list(coordsxy['xy']).copy()
    d = DataSource.objects.get(id=dataid)
    s_x = float(coords[1][0])
    s_y = float(coords[1][1])
    if d.id == d.event.finder:
        xvar = np.abs(s_x - d.event.xpos)
        yvar = np.abs(s_y - d.event.ypos)
        if (xvar > 3 or yvar > 3):
          # Remove previous values for this point
          return Response(data={'msg': 'Target marker not correctly aligned'}, status=status.HTTP_400_BAD_REQUEST)
    xmean = 0
    ymean = 0
    # Remove previous values for this point
    oldpoints = Datapoint.objects.filter(data=d,user=person)
    oldpoints.delete()
    numpoints = Datapoint.objects.filter(data__event=d.event,user=person).count()
    datestamp = datetime.now()
    reduced = 0
    calave = 0.
    error = ''
    ### Add a datacollection for the current user
    r = d.event.radius
    for k,value in pointtype.items():
        # Background and source
        data = Datapoint(ident=d.event.slug,
                            user=person,
                            pointtype = value,
                            data=d,
                            radius=r,
                            entrymode=mode,
                            tstamp=mktime(d.timestamp.timetuple())
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
            print("save error")
            return Response(data={'msg': 'Error saving data point'}, status=status.HTTP_400_BAD_REQUEST)
    # Slice coord data so we only have calibration stars
    coord = coords[2:]
    # Slice to get source and sky
    basiccoord = np.array(coords[:3])
    nocals = len(coord)
    sc_cal = float(pointsum['sc']) - float(pointsum['bg'])
    # Find out if means have been calculated already, if not do it for the source
    # This step can only happen if we are not at the finder frame
    if numpoints != 0 and d.event.finder != d.id:
        xmean, ymean = measure_offset(d,person,coord)
        # check the source is within this tolerance too
        sc_xpos = d.event.xpos
        sc_ypos = d.event.ypos
        xvar = np.abs(np.abs(sc_xpos-s_x)-np.abs(xmean))
        yvar = np.abs(np.abs(sc_ypos-s_y)-np.abs(ymean))
        if (xvar > 5 or yvar > 5):
            # Remove previous values for this point
            oldpoints = Datapoint.objects.filter(data__id=int(dataid),user=person)
            oldpoints.delete()
            return Response(data={'msg':'Markers not correctly aligned'}, status=status.HTTP_400_BAD_REQUEST)
    for i,value in enumerate(pointsum['cal']):
        xpos = int(float(coord[i][0]))
        ypos = int(float(coord[i][1]))
        newcoord = coord
        nocolls = DataCollection.objects.filter(planet=d.event,person=person,calid=i).count()
        if (nocolls == 0):
            ## Find closest catalogue sources
            if i > 2:
                # Add more datacollections if i is > 2 i.e. after basic 3 have been entered
                cats = CatSource.objects.filter(xpos__lt=xpos-xmean+5,ypos__lt=ypos-ymean+5,xpos__gt=xpos-xmean-5,ypos__gt=ypos-ymean-5,data__event=d.event)
            else:
                cats = CatSource.objects.filter(xpos__lt=xpos+5,ypos__lt=ypos+5,xpos__gt=xpos-5,ypos__gt=ypos-5,data__event=d.event)
            if cats:
                dcoll = DataCollection(person=person,planet=d.event,complete=False,calid=i,source=cats[0])
            else:
                dcoll = DataCollection(person=person,planet=d.event,complete=False,calid=i)
            dcoll.display = True
            dcoll.save()
        else:
            dcoll = DataCollection.objects.filter(person=person,planet=d.event,calid=i)[0]
        data = Datapoint(ident=d.event.slug,
                            user=person,
                            pointtype = 'C',
                            data=d,
                            radius=r,
                            entrymode='W',
                            tstamp=mktime(d.timestamp.timetuple())
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
            return Response(data={'msg': 'Error saving'}, status=status.HTTP_400_BAD_REQUEST)
        calave = calave +sc_cal/(value - float(pointsum['bg']))/float(nocals)
    else:
        nomeas = Datapoint.objects.filter(user=person).values('taken').annotate(Count('taken')).count()
        noplanet = DataCollection.objects.filter(person=person).values('planet').annotate(Count('person')).count()
        ndecs = Decision.objects.filter(person=person,current=True).count() # filter: ,planet=d.event
        unlock = False
        nunlock = 0
        resp = achievementscheck(person,d.event,nomeas,noplanet,nocals,ndecs,0)
        msg = '<br />'
        for item in resp:
            if messages.SUCCESS == item['code'] :
                msg += "<img src=\""+settings.STATIC_URL+item['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />"

        if resp:
            lines['msg'] = 'Achievement unlocked {}'.format(msg)
        else:
            lines['msg'] = 'Measurements saved'

        return Response(data=lines, status=status.HTTP_200_OK)

def datagen(slug,user):

    # Extract name of exoplanet from the dataset
    event = Event.objects.get(slug=slug)

    # Collect sources
    sources = DataSource.objects.filter(event=event).order_by('timestamp')

    numsuper,fz,mycals,std,nodata = supercaldata(user,slug)
    print(numsuper,fz,mycals,std,nodata)

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

def calstats(user, planet, decs, numobs):

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
    calvals_array = np.array(np.vstack(calvals_data))

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
            if len(calpoints) == numobs:
                # Append calpoints
                calslist.append(list(calpoints))

        # Loops through calslist
        if len(calslist) > 0:
            # if settings.LOCAL_DEVELOPMENT: logger.debug("\033[94mWe have calibrators\033[1;m")

            # Stacks the values
            calstack = np.array([])
            calstack = np.vstack(calslist)
            #logger.debug('calstack=',calstack)

            # This throws a wobbly sometimes
            cc = (sc-bg)/(calstack-bg)
            calibs.append(cc.tolist())

    # Create normalisation function
    norm_a = lambda a: np.mean(np.r_[a[:3],a[-3:]])
    mycals = []

    #logger.debug('calibs=', calibs)

    try:
        # Stacks all of the calibrators
        cala = np.vstack(calibs)
        #logger.debug('cala=', cala)

        # Normalises stacked calibrators
        norms = np.apply_along_axis(norm_a, 1, cala)
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
    norm_alt = np.mean(norm1,axis=0)
    variance = np.var(norm1,axis=0)
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


    # Extract the name of the planet being analysed
    planet = Event.objects.get(slug=planet)

    # Pull all of the decisions into an object
    decs = Decision.objects.values_list('person','source').filter(value='D', current=True, planet=planet, source__datacollection__display=True).annotate(Count('source'))
    if decs:
        return calstats(user, planet.slug, decs, planet.numobs)
    else:
        return False

def calibratemydata(code,user):
    #cs = Datapoints.objects.filter(pointtype='C',user=user).order_by('coorder__calid')
    ds = DataSource.objects.filter(event__slug=code).order_by('timestamp')
    stars = DataCollection.objects.filter(planet__slug = code,person=user).values_list('source',flat=True)
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


def myaverages(code,person):
    ds = DataSource.objects.filter(event__slug=code).order_by('timestamp').values_list('id',flat=True)
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
        e = Event.objects.filter(slug=code)[0]
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
                points = Datapoint.objects.filter(user=person,data__event__slug=code).order_by('data__timestamp')
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
                normmean = np.mean(normcals,axis=0)
                return list(normmean/np.max(normmean))
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
        dc = DataCollection.objects.filter(~Q(source=None),planet__slug=code).values_list('source__id',flat=True).distinct()
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
                        decvalue_full = Decision.objects.filter(source=c,planet__slug=code,current=True).values_list('value').annotate(total=Count('id'))
                        decvalue = dict((str(key),value) for key,value in decvalue_full)
                        source = CatSource.objects.get(id=c)
                        cat_item = {'sourcename':str(source.name),'catalogue':str(source.catalogue),'sourceid': str(c),'include':source.final}
                        cat_item['decisions'] = decvalue
                        cats.append(cat_item)
                        callist.append(c)
    else:
        dc = DataCollection.objects.filter(~Q(source=None),person=person,planet__slug=code).order_by('calid')
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
                            decvalue = Decision.objects.filter(source=c.source,person=person,planet__slug=code,current=True)[0].value
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



def leastmeasured(code):
    coords = []
    e = Event.objects.get(slug=code)
    dc = DataCollection.objects.values('source').filter(~Q(source=None),planet=e).annotate(count = Count('source')).order_by('count')[:4]
    for coll in dc:
        s = CatSource.objects.get(id=coll['source'])
        coords.append({'x':int(s.xpos),'y':int(s.ypos),'r':int(e.radius)})
    return coords
