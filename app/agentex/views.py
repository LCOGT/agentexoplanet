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
from django.views.generic import DetailView, ListView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from itertools import chain
from time import mktime
import json
import logging
import numpy as np

from agentex.serializers import MeasurementSerializer
from agentex.models import *
from agentex.models import decisions
from agentex.forms import DataEntryForm
import agentex.dataset as ds
from agentex.datareduc import savemeasurement, datagen

from agentex.agentex_settings import planet_level
from agentex.datareduc import *

guestuser = 2

logger = logging.getLogger('agentex')

class DataEntry(DetailView):
    model = DataSource

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object.event
        person = self.request.user
        context['progress'] = checkprogress(person, event.slug)
        context['least_data'] = leastmeasured(event.slug)
        context['coords'] = previous_meas_coords(event, person)
        context['webinput'] = True
        context['DATA_URL'] = settings.DATA_URL
        return context


class EventView(DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['progress'] = checkprogress(self.request.user, self.object.slug)
        return context


class EventList(ListView):
    model = Event
    queryset = Event.objects.filter(enabled=True)


class AddValuesView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def post(self, request, format=None):
        serializer = MeasurementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            resp = savemeasurement(request.user, data,serializer.validated_data['id'],'W')
            return resp
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    #return render_to_response('agentex/index.html', context_instance=RequestContext(request))
    return render(request, 'agentex/index.html', {})

def previous_meas_coords(event, user):
    ds = DataSource.objects.filter(event=event, datapoint__user=user).distinct()
    if ds.count() > 0:
        cals = Datapoint.objects.values('xpos','ypos').filter(data=ds[0],pointtype='C',user=user).order_by('coorder__calid')
        prev = Datapoint.objects.values('xpos','ypos').filter(user=user,data=ds[0]).order_by('coorder__calid')
        data =  { 'source': prev.filter(pointtype='S')[0],
                             'bg'  : prev.filter(pointtype='B')[0],
                             'cal'  : list(cals) ,
                             'id'  : ds[0],
                             }

        return data
    else:
        return False

def next_datasource(request, slug):
    try:
        ds = DataSource.objects.filter(~Q(datapoint__user=request.user), event__slug=slug).latest('pk')
    except DataSource.DoesNotExist:
        return HttpResponseRedirect(reverse('my-graph',kwargs={'slug' : slug}))
    return HttpResponseRedirect(reverse('addvalue',kwargs={'pk':ds.pk}))

def read_manual_check(request):
    if (request.POST.get('read_manual','')=='true' and request.user.is_authenticated):
        o = personcheck(request)
        print(o)
        resp = achievementunlock(o,None,'manual')
        if messages.SUCCESS == resp['code'] :
            messages.add_message(request, messages.SUCCESS, "Achievement unlocked<br /><img src=\""+settings.STATIC_URL+resp['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />")
    return HttpResponseRedirect(reverse(target))


# measurements, planets, calibrators descisions

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

def graphview_simple(request,slug):
# If graphview is simple

    # Stores the name of the observer from the request in variable o
    o = personcheck(request)

    # Stores the number of completed datasets with the total
    progress = checkprogress(o,slug)

    # See first if statement
    n = 0

    # Creates a dataset object for the user
    d1 = ds.Dataset(slug,o.username)

    # Returns information in 2 lists for the data being analysed as well as information on the datapoints
    data,points = d1.my_data()#my_data(o,slug)

    # Returns list of data collections based on the exoplanet being analysed
    dc = DataCollection.objects.filter(person=o,planet=d1.planet)

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
    classif = classified(o,slug)

    # Render the findings
    return render(request, 'agentex/graph_flot.html', {'event':d1.planet,
                                                            'data':data,
                                                            'n':n,
                                                            'sources':cats,
                                                            'classified':classif,
                                                            'progress' : progress})

@login_required
def graphview_ave(request,code,mode,calid):
    # If the mode is average rather than simple

    # Stores the name of the observer from the request in variable o
    o = personcheck(request)

    # Stores the number of completed datasets with the total
    progress = checkprogress(o,code)

    # See first if statement
    n = 0

    # Define empty list to store data
    data = []

    # get and restructure the average data JS can read it nicely
    # Stores the date and time at this instance
    now = datetime.now()

    # Calls photometry function and stores results

    cals,normcals,sb,bg,dates,stamps,ids,cats = photometry(code,o,progress)

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
    dec = Decision.objects.values('source__name').filter(person=o,planet__slug=code,value__in=['D','N','B','P','R','S'],current=True).annotate(count=Count('source')).order_by('count')

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
        mychoice = Decision.objects.values('value').filter(person=o,planet__slug=code,value__in=['D','N','B','P','R'],source__name=currentcal['sourcename'])
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
    resp = achievementscheck(o,planet,0,0,0,len(cats),0)
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
def graphview_advanced(request,slug):

    # Stores the name of the observer from the request in variable o
    o = personcheck(request)

    # Stores the number of completed datasets with the total
    progress = checkprogress(o,slug)

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

    return render(request, 'agentex/graph_advanced.html', {'event':Event.objects.filter(slug=slug)[0],
                                                                    'framedata':line,
                                                                    'target':DataSource.objects.filter(event__name=code)[0].target,                                                                    'progress' : progress})



def graphsuper(request,slug):
    # Construct the supercalibrator lightcurve

    # Extract name of exoplanet from the dataset
    event = Event.objects.get(slug=slug)

    user = request.user

    # Call datagen to generate realtime data
    data = datagen(slug,user)

    ###### Setting nodata to True and not showing each person their own data, but just for now
    return render(request, 'agentex/graph_super.html', {'event':event,
                                                                'data':data,
                                                                'numsuper':13,
                                                                'nodata' : True})

@login_required
def measurementsummary(request,code,format):
    ####################
    # Return a measument data set based on event code and having either 'json' or 'xml' format
    data = []
    maxpixel = 1024
    csv =""
    o = request.user
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
        maxcals = DataCollection.objects.filter(person=o[0].user,planet__slug=code).aggregate(Max('calid'))['calid__max']
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
    return

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
        newx.append(np.floor(float(entry)*size))
    return newx

def ismypoint(person,datauser):
    if person == datauser:
        return True
    else:
        return False

def classified(o,code):
    dcs = Decision.objects.values('source').filter(person=o,planet__slug=code).annotate(last = Max('taken'))
    dips = Decision.objects.filter(taken__in=[d['last'] for d in dcs],person=o,planet__slug=code,value='D').count()
    classifications = Decision.objects.values('source').filter(person=o,planet__slug=code).annotate(Count('value')).count()
    totalcalibs = DataCollection.objects.values('source').filter(person=o,planet__slug=code).annotate(Count('display')).count()
    return {'total' : totalcalibs, 'done':classifications,'dip':dips}

def checkprogress(person,code):
    n_analysed = Datapoint.objects.filter(user=person, data__event__slug=code,pointtype='S').count()
    n_sources = DataSource.objects.filter(event__slug=code).count()
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
