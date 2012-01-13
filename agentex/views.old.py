from django.utils import simplejson
from django.utils.encoding import smart_unicode
from django.core.serializers import serialize
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION
from django.db.models import Count,Avg,Min,Max,Variance, Q, Sum
from django.contrib import messages
import urllib2
from xml.dom.minidom import parse
from math import sin,acos,fabs,sqrt
from numpy import *
import pyfits
from datetime import datetime,timedelta
from calendar import timegm
from time import mktime
from math import floor,pi,pow
from itertools import chain
from numpy import array

from django.contrib.auth.models import User
from odin.dataexplorer.models import Target, Event, Datapoint, DataSource, DataCollection,CatSource, Decision, Achievement, Badge
from odin.dataexplorer.models import decisions
from odin.obsapp.models import Observer
from odin.dataexplorer.forms import DataEntryForm, RegisterForm

from odin.settings import DATA_LOCATION,DATA_URL,MEDIA_URL
from odin.dataexplorer.agentex_settings import planet_level

guestuser = 2

def index(request):  
    return render_to_response('dataexplorer/index.html', context_instance=RequestContext(request))

def briefing(request):
    return render_to_response('dataexplorer/briefing.html', context_instance=RequestContext(request))

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        # Check if User has already registered with same username or email address
        if form.is_valid():
            if len(User.objects.filter(username=form.cleaned_data['username'])) == 0:
                user = User.objects.create_user(form.cleaned_data['username'],form.cleaned_data['emailaddress'],form.cleaned_data['password'])
                user.first_name=form.cleaned_data['firstname']
                user.last_name=form.cleaned_data['lastname']
                user.save()
                o = Observer(user=user)
                o.save()
                messages.success(request,"Your account has been created")
                return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))
            else:
                messages.error(request,"This username has already been registered, please choose another")
                return render_to_response("register.html",{'form': form},context_instance=RequestContext(request))
        else:
            return render_to_response("register.html",{'form': form},context_instance=RequestContext(request))
    else:
        return render_to_response("register.html",{'form': RegisterForm()},context_instance=RequestContext(request))

@login_required
def profile(request):
    a = Achievement.objects.filter(person=request.user).order_by('badge')
    nomeas = Datapoint.objects.filter(user=request.user).values('taken').annotate(Count('taken')).count()
    noplanet = DataCollection.objects.filter(person=request.user).values('planet').annotate(Count('person')).count()
    completed = DataCollection.objects.values('planet').filter(person=request.user).annotate(Count('complete')).count()
    #ndecs = Decision.objects.filter(person=request.user,planet=d[0].event,current=True).count()
    badgelist = Badge.objects.exclude(id__in=[b.badge.id for b in a]).order_by('name')
    return render_to_response("profile.html",{'unlocked':a,'badges':badgelist,'planets':noplanet,'measurements':nomeas,'completed':completed},context_instance=RequestContext(request))

#@login_required
def target(request):  
    data = []
    events = Event.objects.filter(enabled=True)
    for e in events:
        if (request.user.is_authenticated()):
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
    return render_to_response('dataexplorer/target.html', {'data':data},context_instance=RequestContext(request))

@login_required
def addvalue(request,code):
    form = DataEntryForm()
    if (request.user.is_authenticated()):
        person = request.user
    else:
        person = guestuser
    o = Observer.objects.filter(user=person)
    progress = checkprogress(person,code)
    if (progress['done'] >= progress['total']):
        dcolls = DataCollection.objects.filter(person=person,planet__name=code)
        dcolls.update(complete=True)
    ###### Has the user selected to use the web interface
    ###### Default for anonymous is always web interface
    if (person != guestuser):
        try:
            webin = o[0].dataexploreview
        except:
            webin = True
    else:
        webin = True
    least_coords = leastmeasured(code)
    if (request.POST):
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
                url = reverse('odin.dataexplorer.views.addvalue',args= [DataSource.objects.get(id=id).event.name])
                return HttpResponseRedirect(url)
            x = map(float,x)
            y = map(float,y)
            coords = zip(x,y)
            dataid = request.POST.get('dataid','')
            resp = savemeasurement(person,pointsum,coords,dataid,entrymode)
            messages.add_message(request, resp['code'], resp['msg'])
            if webin == False:
                url = "%s?%s" % (reverse('odin.dataexplorer.views.addvalue',args= [DataSource.objects.get(id=id).event.name]),"input=manual")
            else:
                url = reverse('odin.dataexplorer.views.addvalue',args= [DataSource.objects.get(id=id).event.name])
             #messages.success(request, "Measurement successfully added")
            return HttpResponseRedirect(url)
        else:
            return render_to_response('dataexplorer/dataentry.html', {'data':DataSource.objects.get(id=id),'form':form,'data_url':DATA_URL}, context_instance=RequestContext(request))
    else:
        nextcal = request.GET.get('next',False)
        ############ This condition is active when a user edits the frame
        # Find the data sources for the given code
        source = DataSource.objects.filter(event__name=code)
        length = source.count()
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
                    url = reverse('odin.dataexplorer.views.addvalue',args= [DataSource.objects.get(id=id).event.name])
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
                url = reverse('odin.dataexplorer.views.addvalue',args= [code])
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
            return render_to_response('dataexplorer/dataentry.html',{'data':d,
                                                                    'next':dnext,
                                                                    'points':coords,
                                                                    'update':True,
                                                                    'webinput':webin,
                                                                    'progress':progress,
                                                                    'form':form,
                                                                    'calibrators':calibs,
                                                                    'least_data':least_coords,
                                                                    'data_url':DATA_URL},
                                    context_instance=RequestContext(request))                             
        else:
            ######## User is being given a new frame not editing data  
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
                        msg += "<img src=\""+MEDIA_URL+item['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />"
                        messages.success(request,msg)
                
                return HttpResponseRedirect(reverse('my-graph',args=[code]))

                return render_to_response('dataexplorer/dataentry.html',
                                        {'event': e,
                                        'complete':complete,
                                        'progress':progress,
                                        'points':Datapoint.objects.filter(user=person,pointtype='S',data__event=e).order_by('data__timestamp'),
                                        'data_url':DATA_URL,
                                        'numplanets':numplanets,},
                                        context_instance=RequestContext(request))            
            else:
                mylist = Datapoint.objects.filter(user=person,pointtype='S').values_list('data',flat=True)
                ### if person does not have a DataCollection it is their first measurement
                if (DataCollection.objects.filter(planet__name = code,person=person).count() == 0):
                    e = Event.objects.get(name=code)
                    d = DataSource.objects.filter(event__name=code,id=e.finder)[0]
                    try:
                        dold = d.id
                        first = True   
                    except:
                        messages.error(request,"Finderchart cannot be found")
                        raise Http404    
                elif  person == guestuser:
                    d = DataSource.objects.filter(event__name=code).annotate(count=Count('datapoint')).order_by('-count')[0]
                    dold = d.id
                    first = True
                else:
                    try:
                        available = DataSource.objects.filter(event__name=code).exclude(id__in=[p for p in mylist]).annotate(count=Count('datapoint')).order_by('-count')  
                        dold = Datapoint.objects.values_list('data__id',flat=True).filter(user=person,data__event__name=code,pointtype='C').annotate(max =Max('coorder__calid')).order_by('-max','-taken')[0]
                    # Find position in set of DataSources
                        d = available[0]
                        first = False
                    except:
                        messages.error(request,"User has a data collection but no points!")
                        raise Http404
                cals = Datapoint.objects.values_list('xpos','ypos').filter(data=dold,pointtype='C',user=person).order_by('coorder__calid')
                calibs = []
                if cals:
                    for c in cals:
                        calibs.append({'x' : int(c[0]) , 'y' : int(c[1])})
                otherpoints = Datapoint.objects.filter(~Q(user=person),pointtype='C',data=d.id)
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
                             'radius' : d.event.radius
                             }
                else:
                    coords = False
                if person == guestuser:
                    progress = {'percent'   : "0",
                                'done'      : 0,
                                'total'     : n_sources,}
                return render_to_response('dataexplorer/dataentry.html',
                                        {'data':d,
                                        'complete':complete,
                                        'update':False,
                                        'webinput':webin,
                                        'progress':progress,
                                        'form':form,
                                        'calibrators':othercals,
                                        'points':coords,
                                        'least_data':least_coords,
                                        'data_url':DATA_URL},
                                        context_instance=RequestContext(request))        


def savemeasurement(person,pointsum,coords,dataid,entrymode):
    # Only update the user's preference if they change it
    o = Observer.objects.filter(user=person)
    try:
        if (entrymode == 'manual' and o[0].dataexploreview == True):
            o.update(dataexploreview=False)
            messages.success(request, "Setting changed to use manual view")
        elif (entrymode == 'dataexplorer' and o[0].dataexploreview == False):
            o.update(dataexploreview=True)
            messages.success(request, "Setting changed to use web view")
    except:
        print "Having problems with"
    mode = {'dataexplorer':'W','manual':'M'}
    pointtype = {'sc':'S','bg':'B'}
    d = DataSource.objects.filter(id=int(dataid))
    s_x = float(coords[1][0])
    s_y = float(coords[1][1])
    xmean = 0
    ymean = 0 
    # Remove previous values for this point
    oldpoints = Datapoint.objects.filter(data__id=int(dataid),user=person)
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
        data = Datapoint(user=person,
                            pointtype = value,
                            data=d[0], 
                            radius=r,
                            entrymode=mode[entrymode],)
        if k == 'sc':
            coord = coords[1]
            data.offset = 0
        elif k == 'bg':
            coord = coords[0]
            data.offset = int(sqrt((s_x - float(coord[0]))**2 + (s_y - float(coord[1]))**2))
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
    basiccoord = array(coord[:3])
    nocals = len(coord)
    sc_cal = float(pointsum['sc']) - float(pointsum['bg'])
    # Find out if means have been calculated already, if not do it for the source
    # This step can only happen if we are not at the finder frame 
    if numpoints != 0 and d[0].event.finder != d[0].id:
        xmean, ymean = measure_offset(d,person,basiccoord)
        # check the source is within this tolerance too
        sc_xpos = d[0].event.xpos
        sc_ypos = d[0].event.ypos
        xvar = abs(abs(sc_xpos-s_x)-abs(xmean))
        yvar = abs(abs(sc_ypos-s_y)-abs(ymean))
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
                cats = CatSource.objects.filter(xpos__lt=xpos-xmean+5,ypos__lt=ypos-ymean+5,xpos__gt=xpos-xmean-5,ypos__gt=ypos-ymean-5)
            else:
                cats = CatSource.objects.filter(xpos__lt=xpos+5,ypos__lt=ypos+5,xpos__gt=xpos-5,ypos__gt=ypos-5)
            if cats:
                dcoll = DataCollection(person=person,planet=d[0].event,complete=False,calid=i,source=cats[0])
            else:
                dcoll = DataCollection(person=person,planet=d[0].event,complete=False,calid=i)
            dcoll.save()
        else:
            dcoll = DataCollection.objects.filter(person=person,planet=d[0].event,calid=i)[0]
        data = Datapoint(user=person,
                            pointtype = 'C',
                            data=d[0], 
                            radius=r,
                            entrymode=mode[entrymode])
        data.value= float(value)
        data.xpos = xpos
        data.ypos = ypos
        data.offset = int(sqrt((s_x - float(coord[i][0]))**2 + (s_y - float(coord[i][1]))**2))
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
                msg += "<img src=\""+MEDIA_URL+item['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />"
                unlock = True
                nunlock += 1

        if unlock :
            if nunlock > 1 : return {'msg': 'Achievements unlocked'+msg, 'code': messages.SUCCESS}
            else : return {'msg': 'Achievement unlocked'+msg, 'code': messages.SUCCESS}
        return {'msg': 'Measurements saved', 'code': messages.SUCCESS}

def measure_offset(d,person,basiccoord):
    # Find the likely offset of this new calibrator compared to the basic ones and find any sources within 5 pixel radius search
    finderid = d[0].event.finder
    finderdp = Datapoint.objects.values_list('xpos','ypos').filter(user=person,data__id=finderid,pointtype='C',coorder__calid__lt=3).order_by('coorder__calid')
    finder = basiccoord - array(finderdp)
    t = transpose(finder)
    xmean = mean(t[0])
    ymean = mean(t[1])
    return xmean,ymean



def read_manual_check(request):
	if (request.POST.get('read_manual','')=='true' and request.user.is_authenticated()):
		o = personcheck(request)
		resp = achievementunlock(o.user,None,'manual')
		if messages.SUCCESS == resp['code'] :
			messages.add_message(request, messages.SUCCESS, "Achievement unlocked<br /><img src=\""+MEDIA_URL+resp['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />")
		
	return HttpResponseRedirect(reverse('odin.dataexplorer.views.target'))
		


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
                object_repr     = smart_unicode(newa), 
                action_flag     = ADDITION,
                change_message  = 'Achievement automatically unlocked'
            )
            return {'msg': 'Achievement unlocked', 'image':"%s" % badge[0].image, 'code': messages.SUCCESS }
        except:
            return {'msg' : 'Achievement save error', 'image':"%s" % badge[0].image, 'code': messages.ERROR }
    else:
        return {'msg' : 'Already has this badge', 'image': '', 'code': messages.WARNING }

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
        old.update(current=False)
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
def graphview(request,code,mode,calid):
    #measurement = Datapoint.objects.filter(taken=date,data__event__name=code)
    #calibrate(measurement)
    o = personcheck(request)
    progress = checkprogress(o.user,code)
    planet = Event.objects.filter(name=code)[0]
    data = []
    if mode == 'simple':
        sources = DataSource.objects.filter(event__name=code).order_by('timestamp')
        points  = Datapoint.objects.filter(data__event__name=code,user=o.user)
        # points = Datapoint.objects.filter(~Q(pointtype='R'),data__event__name=code).values('data__id','data__timestamp').order_by('data__timestamp')
        # mypoints = Datapoint.objects.filter(~Q(pointtype='R'),data__event__name=code,user=o[0])
        n = 0
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
        else:
            cats = None
        classif = classified(o,code)
        return render_to_response('dataexplorer/graph_flot.html', {'event':planet,
                                                                'data':data,
                                                                'n':n,
                                                                'sources':cats,
                                                                'classified':classif,
                                                                'progress' : progress,
                                                                'target':DataSource.objects.filter(event__name=code)[0].target}, 
                                                                context_instance=RequestContext(request))
    elif mode == 'ave':
        # get and restructure the average data JS can read it nicely
        now = datetime.now()
        #cals,normcals,sb,bg,dates,stamps,ids,cats = myaverages(code, o.user)
        cals,normcals,sb,bg,dates,stamps,ids,cats = averagecals(code, o.user)
        numcals = len(normcals)
        for i,id in enumerate(ids):
            #mycalibs = []
            calibs = []
            normcalibs = []
            for j in range(0,numcals):
                calibs.append([cals[j][i],cats[j]['order']])
                #mycalibs.append(mycals[j][i])
                normcalibs.append(normcals[j][i])
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
            data.append(line)
        planet = Event.objects.filter(name=code)[0]        
        ### Make sure person gets a different calibrator (that they haven't classified) after each POST
        currentcal = None
        dec = Decision.objects.values('source__name').filter(person=o.user,planet__name=code,value__in=['D','N','B','P','R','S'],current=True).annotate(count=Count('source')).order_by('count')
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
        print datetime.now() - now
        classif = classified(o,code)
        resp = achievementscheck(o.user,planet,0,0,0,len(cats),0)
        unlock = False
        nunlock = 0
        msg = '<br />'
        
        for item in resp:
            if messages.SUCCESS == item['code'] :
                msg += "<img src=\""+MEDIA_URL+item['image']+"\" style=\"width:96px;height:96px;\" alt=\"Badge\" />"
                unlock = True
                nunlock += 1

        if unlock :
            if nunlock > 1 : msg = 'Achievements unlocked'+msg
            else : msg = 'Achievement unlocked'+msg
            messages.add_message(request, messages.SUCCESS, msg)


        return render_to_response('dataexplorer/graph_average.html', {'event': planet,
                                                                'data':data,
                                                                'sources':cats,
                                                                'calid': currentcal,
                                                                'prevchoice' : prev,
                                                                'classified':classif,
                                                                'progress' : progress,
                                                                'target':DataSource.objects.filter(event=planet)[0].target},
                                                                context_instance=RequestContext(request))
            
    elif mode == 'super':
        # Construct the supercalibrator lightcurve
        numsuper, normvals, std,radiusratio = supercaldata(planet)
        #print numsuper
        e = Event.objects.get(name=code)
        sources = DataSource.objects.filter(event=e).order_by('timestamp')
        n = 0
        classif = classified(o,code)
        if len(normvals) == e.numobs :
            for i,s in enumerate(sources):
                line = {
                        'id'        : "%i" % s.id,
                        'date'      : s.timestamp.isoformat(" "),
                        'datestamp' : timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,
                        'data'      : {
                                        'mean' : normvals[i],
                                        'std'  : std[i],
                            },
                        }
                data.append(line)
        else:
            data = None
        return render_to_response('dataexplorer/graph_super.html', {'event':planet,
                                                                    'data':data,
                                                                    'numsuper':numsuper,
                                                                    'planetradius':radiusratio,
                                                                    'target':sources[0].target}, context_instance=RequestContext(request))
    elif mode == 'advanced':
        opt = {'S' :'source','C':'calibrator','B':'sky'}
        if 'dataid' in request.GET:
            dataid = request.GET.get('dataid','')
        else:    
            dataid = Datapoint.objects.filter(user=o[0].user).order_by('taken')[0].data.id
        try:
            s = DataSource.objects.filter(id=dataid)[0]
        except:
            raise Http404  
        ps  = Datapoint.objects.filter(~Q(pointtype = 'R'),data = s).order_by('-pointtype')
        datalist = [{'mine': ismypoint(o[0],dp.user),'x' : dp.xpos,'y' : dp.ypos, 'r' : dp.radius, 'value' : "%.0f" % dp.value,'type':opt[dp.pointtype]} for dp in ps]
        line = {
                'id'        : "%i" % s.id,
                'date'      : s.timestamp.isoformat(" "),
                'datestamp' : timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,
                'data'      : datalist,
                }
        return render_to_response('dataexplorer/graph_advanced.html', {'event':Event.objects.filter(name=code)[0],
                                                                        'framedata':line,
                                                                        'target':DataSource.objects.filter(event__name=code)[0].target,
                                                                        'progress' : progress}, context_instance=RequestContext(request))


def infoview(request,code):
    ds = DataSource.objects.filter(event__name=code)[:1]
    try:
        data = ds[0]
    except:
        raise Http404
    return render_to_response('dataexplorer/info.html', {'object' : data}, context_instance=RequestContext(request))
    
def fitsanalyse(request):
    now = datetime.now()
    if (request.user.is_authenticated()):
        person=request.user
    else:
        person = User.objects.filter(id=guestuser)[0]
    # Flag poor quality result
    #print datetime.now() - now
    flag = ''
    # Extract variables passed from the image
    # Order of variables sent is 'bg','source','cal1','cal2'...
    x = request.POST.get('x','').split(',')
    y = request.POST.get('y','').split(',')
    if (len(x) < 3 or len(y) < 3):
        response = {'message' : 'Please submit calibration, blank sky and source apertures.'}
        return HttpResponse(simplejson.dumps(response),mimetype='application/javascript')
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
    #    return HttpResponse(simplejson.dumps(response),mimetype='application/javascript')
    # Check all apertures are away from frame edge
    d = DataSource.objects.filter(id=int(dataid))[:1]
    r = d[0].event.radius
    for co in coords:
        xi = co[0]
        yi = co[1]
        if (xi-r < 0 or xi+r >= d[0].max_x or yi-r < 0 or yi+r > d[0].max_y ):
            response = {'message' : 'Please make sure your circles are fully within the image'}
            return HttpResponse(simplejson.dumps(response),mimetype='application/javascript')

    #print datetime.now() - now
    # Grab a fits file
    dfile = "%s%s" % (DATA_LOCATION,d[0].fits)
    #print dfile
    dc = pyfits.getdata(dfile,header=False)
    #print datetime.now() - now
    
    # Find all the pixels a radial distance r from x0,y0
    for co in coords:
        # Sum for this aperture
        sum = 0
        numpix = 0
        x0 = int(floor(co[0]))
        y0 = int(floor(co[1]))
        ys = y = y0 -r
        ye = y0 +r
        vline = list()
        hline = list()
        while (y < ye):
            angle = fabs(1.*(y-y0)/r)
            dx = int(sin(acos(angle))*r)
            x = xs = x0 - dx
            xe = x0 + dx
            while (x < xe):
                sum += float(dc[y][x])
                x += 1
                if (x == x0):
                    hline.append(float(dc[y][x]))
                if (y == y0):
                    vline.append(float(dc[y][x]))
                    #print "x = %s, y= %s val=%s" % (x,y,float(dc[y][x]))
                numpix += 1
            y += 1
        linex.append(hline)
        liney.append(vline)
        counts.append(sum)
    #print datetime.now() - now
    
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
    #print (datetime.now() - now)
    # save measurement data on the backend automatically
    entrymode = request.POST.get('entrymode','M')
    resp = savemeasurement(person,pointsum,coords,dataid,entrymode)
    if  resp['code'] == messages.ERROR:
        lines = {'error':  resp['msg']}
    else:
        messages.add_message(request, resp['code'], resp['msg'])
    return HttpResponse(simplejson.dumps(lines,indent = 2),mimetype='application/javascript')
        
def measurementsummary(request,code,format):
    ####################
    # Return a measument data set based on event code and having either 'json' or 'xml' format
    data = []
    maxpixel = 1024
    csv =""
    if (request.user.is_authenticated()):
        o = Observer.objects.filter(user=request.user)
    else:
        o = Observer.objects.filter(user=guestuser)
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
        sources = array(mypoints.filter(pointtype='S').values_list('value',flat=True))
        ids = mypoints.filter(pointtype='S').values_list('data__id',flat=True)
        bg = array(mypoints.filter(pointtype='B').values_list('value',flat=True))
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
        return HttpResponse(simplejson.dumps(datapoints,indent=2),mimetype='application/javascript')
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
        return HttpResponse(simplejson.dumps(datapoints,indent=2),mimetype='application/javascript')
    elif (format == 'xhr' and options == 'super'):
        # Construct the supercalibrator lightcurve
        planet = Event.objects.filter(name=code)[0]
        numsuper, normvals, std,radiusratio = supercaldata(planet)
        sources = DataSource.objects.filter(event=planet).order_by('timestamp')
        dates = []
        for s in sources:
            dates.append(timegm(s.timestamp.timetuple())+1e-6*s.timestamp.microsecond,)
        datapoints = {'normalised' : normvals, 'dates':dates, 'std':std}
        return HttpResponse(simplejson.dumps(datapoints),mimetype='application/javascript')
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
        return HttpResponse(simplejson.dumps(line,indent = 2),mimetype='application/javascript')
    else:
        points = Datapoint.objects.filter(data__event__name=code).values_list('value','data__timestamp','data__id').order_by('data__timestamp')
        sources = DataSource.objects.filter(event__name=code).order_by('timestamp')
        mypoints = Datapoint.objects.filter(pointtype='S',data__event__name=code,user=o[0]).annotate(mean=Avg('value'))
        for s in points.filter(pointtype='S'):
            line = {
                    'id'        : s[2],
                    'date'      : s[1].isoformat(" "),
                    'datestamp' : timegm(s[1].timetuple())+1e-6*s[1].microsecond,
                    'values'    : {
                                        'source': '%f' % s[0],
                                        'bg' : "%f" % points.filter(data=s[2],pointtype='B')[0][0],
                                        'cal' : list(points.filter(data=s[2],pointtype='C').order_by('coorder__calid').values_list('value',flat=True)),
                                }
                    }
            data.append(line)
        if format == 'json':
            return HttpResponse(simplejson.dumps(data,indent = 2),mimetype='application/javascript')
        elif format == 'xml':
            return render_to_response('dataexplorer/data_summary.xml',{'data':data},mimetype="application/xhtml+xml")
        elif format == 'csv':
            csv = "Date of observation, total source counts, total background counts, total counts calibrator 1, total counts calibrator 2, ...\n"
            for s in points.filter(pointtype='S'):
                csv += "%s," % s[1].strftime('%Y-%m-%d %H:%M')
                csv += "\t"
                csv +=  '%.0f,' % s[0]
                csv += "\t"
                csv +=  "%.0f, " % points.filter(data=s[2],pointtype='B')[0][0]
                for cal in list(points.filter(data=s[2],pointtype='C').order_by('coorder__calid').values_list('value',flat=True)):
                    csv += "%.0f, " % cal
                csv +="\n"
            return HttpResponse(csv,mimetype='text/csv')

def calibratemydata(code,user):
    #cs = Datapoints.objects.filter(pointtype='C',user=user).order_by('coorder__calid')
    ds = DataSource.objects.filter(event__name=code).order_by('timestamp')
    stars = DataCollection.objects.filter(planet__name = code,person=user).values_list('source',flat=True)
    cals = []
    mycals = []
    dates = []
    stamps = []
    timestamps = []
    ids = []
    scA = []
    bgA = []
    for i,st in enumerate(stars):
        vals = []
        myvals = []
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
                myvals.append((sb-bg)/(mypoint[0].value-bg))
            else:
                myvals.append(0.0)
            if i == 0:
                dates.append(d.timestamp.isoformat(" "))
                stamps.append(timegm(d.timestamp.timetuple())+1e-6*d.timestamp.microsecond)
                timestamps.append(d.timestamp)
                ids.append(d.id)
                scA.append(sb)
                bgA.append(bg)
        maxvals = r_[vals[:3],vals[-3:]]
        nz = maxvals.nonzero()
        maxval = mean(maxvals[nz])
        cals.append(list(vals/maxval)) 
        mycals.append(list(myvals/maxval))
    return cals,mycals,scA,bgA,dates,stamps,ids
    
def myaverages(code,person):
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
    dc = DataCollection.objects.filter(~Q(source=None),person=person,planet__name=code).order_by('calid')
    cs = CatSource.objects.filter(id__in=[c.source.id for c in dc]).annotate(count=Count('datacollection__datapoint')).filter(count__gte=e.numobs).values_list('id',flat=True)
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
                    cats.append({'order':'%s' % c.calid,'sourcename':c.source.name,'catalogue':c.source.catalogue,'decision':decvalue})
                    callist.append(c.source.id)
        if callist:
            # Only proceed if we have calibrators in the list (i.e. arrays of numobs)
            ds = DataSource.objects.filter(event__name=code,id__in=ids).order_by('timestamp')
            #points = Datapoint.objects.filter(data__id__in=ids)
            dps = Datapoint.objects.filter(coorder__source__in=cs).values_list('taken','user','data')
            taken,users,data = zip(*dps)
            points = Datapoint.objects.filter(taken__in=taken,user__in=users,data__event__name=code).order_by('data__timestamp')
            scA = points.filter(pointtype='S').values_list('data__id').annotate(ave=Avg('value'))
            #scA = points.filter(pointtype='S',id__in=points).order_by('data__timestamp').values_list('data__id').annotate(Avg('value'))
            bgA = points.filter(pointtype='B').values_list('data__id').annotate(Avg('value'))
            tmp,sc=zip(*scA)
            tmp,bg=zip(*bgA)
            sc = array(sc)
            bg = array(bg)
            for cal in cals:
                val = (sc - bg)/(array(cal)-bg)
                maxval = mean(r_[val[:3],val[-3:]])
                maxvals.append(maxval)
                norm = val/maxval
                normcals.append(list(norm))
            # Find my data and create unix timestamps
            #mydp = DataSource.objects.filter(event__name=code).order_by('timestamp')
            source = ds.filter(datapoint__pointtype='S',datapoint__user=person).annotate(value=Sum('datapoint__value')).values_list('id','value')
            backgs = ds.filter(datapoint__pointtype='B',datapoint__user=person).annotate(value=Sum('datapoint__value')).values('id','value')
            print "lists"
            a = dict(source)
            b = dict(scA)
            print a
            print b
            print dict(b.items() + a.items()).setdefault(0.)
            # sources = Datapoint.objects.values_list('value',flat=True).filter(pointtype='S',data__id__in=ids,user=person).order_by('data__timestamp')
            # backgs = Datapoint.objects.values_list('value',flat=True).filter(pointtype='B',data__id__in=ids,user=person).order_by('data__timestamp')
            # lookup = Datapoint.objects.values_list('data__id', flat=True).filter(pointtype='S',data__event=e,user=person).order_by('data__timestamp')
            # mypoints = Datapoint.objects.filter(pointtype='C',data__id__in=ids,user=person).order_by('data__timestamp')
            mycals = ds.filter(datapoint__pointtype='C',datapoint__user=person)
            numcals = len(cals)
            #mycals = [[] for i in range(numcals)]
            # This is a bottleneck
            unixt = lambda x: timegm(x.timetuple())+1e-6*x.microsecond
            iso = lambda x: x.isoformat(" ")
            times = ds.values_list('timestamp',flat=True)
            stamps = map(unixt,times)
            dates = map(iso,times)
            now = datetime.now()
            #for coll in dc:
                
            # for d in ds:
            #     if d.id in lookup:
            #         index = [i for i,x in enumerate(lookup) if x == d.id][0]
            #         for i,c in enumerate(callist):
            #             myp = mypoints.filter(data=d,coorder__source=c).values_list('value',flat=True)
            #             if myp:
            #                 source = sources[index]
            #                 backg = backgs[index]         
            #                 val = (source-backg)/(myp[0]-backg)/maxvals[i]
            #                 mycals[i].append(val)
            #             else:
            #                 mycals[i].append(0.0)
            #     else:
            #         for i,c in enumerate(callist):
            #             mycals[i].append(0.0)
            print datetime.now() - now
            return cals,normcals,mycals,list(sc),list(bg),dates,stamps,[int(i) for i in ids],cats
    return cals,normcals,mycals,[],[],dates,stamps,[],cats

def averagecals(code,person):
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
    dc = DataCollection.objects.filter(~Q(source=None),person=person,planet__name=code).order_by('calid')
    cs = CatSource.objects.filter(id__in=[c.source.id for c in dc]).annotate(count=Count('datacollection__datapoint')).filter(count__gte=e.numobs).values_list('id',flat=True)
    print datetime.now() - now
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
                    cats.append({'order':'%s' % c.calid,'sourcename':c.source.name,'catalogue':c.source.catalogue,'decision':decvalue})
                    callist.append(c.source.id)
        if callist:
            # Only proceed if we have calibrators in the list (i.e. arrays of numobs)
            ds = DataSource.objects.filter(event__name=code,id__in=ids).order_by('timestamp')
            print datetime.now() - now
            #points = Datapoint.objects.filter(data__id__in=ids)
            #dps = Datapoint.objects.filter(coorder__source__in=cs).values_list('taken','user','data')
            taken = Datapoint.objects.filter(coorder__source__in=cs).values_list('taken',flat=True).distinct()
            print "datapoints"
            print datetime.now() - now
            users = Datapoint.objects.filter(coorder__source__in=cs).values_list('user',flat=True)
            print "users"
            print datetime.now() - now
            print taken.count()
            #taken,users,data = zip(*dps)
            #print "**taken %s users %s data %s" % (len(taken), len(users),len(data))
            # This is too slow use a global average for the source and background
            # points = Datapoint.objects.filter(taken__in=taken,data__in=ds).order_by('data__timestamp')
            points = Datapoint.objects.filter(data__in=ds).order_by('data__timestamp')
            print points.count()
            print "more points"
            scA = points.filter(pointtype='S').values_list('data__id').annotate(ave=Avg('value'))
            #scA = points.filter(pointtype='S',id__in=points).order_by('data__timestamp').values_list('data__id').annotate(Avg('value'))
            bgA = points.filter(pointtype='B').values_list('data__id').annotate(Avg('value'))
            print "point queries done"
            print scA.count()
            tmp,sc=zip(*scA)
            tmp,bg=zip(*bgA)
            print "unzip 2"
            sc = array(sc)
            bg = array(bg)
            print "finished tough stuff"
            print datetime.now() - now
            for cal in cals:
                val = (sc - bg)/(array(cal)-bg)
                maxval = mean(r_[val[:3],val[-3:]])
                maxvals.append(maxval)
                norm = val/maxval
                normcals.append(list(norm))
            # Find my data and create unix timestamps
            #mydp = DataSource.objects.filter(event__name=code).order_by('timestamp')
            # source = ds.filter(datapoint__pointtype='S',datapoint__user=person).annotate(value=Sum('datapoint__value')).values_list('id','value')
            # backgs = ds.filter(datapoint__pointtype='B',datapoint__user=person).annotate(value=Sum('datapoint__value')).values('id','value')
            # # print "lists"
            # # a = dict(source)
            # # b = dict(scA)
            # # print a
            # # print b
            # # print dict(b.items() + a.items()).setdefault(0.)
            # sources = Datapoint.objects.values_list('value',flat=True).filter(pointtype='S',data__id__in=ids,user=person).order_by('data__timestamp')
            # backgs = Datapoint.objects.values_list('value',flat=True).filter(pointtype='B',data__id__in=ids,user=person).order_by('data__timestamp')
            # lookup = Datapoint.objects.values_list('data__id', flat=True).filter(pointtype='S',data__event=e,user=person).order_by('data__timestamp')
            # mypoints = Datapoint.objects.filter(pointtype='C',data__id__in=ids,user=person).order_by('data__timestamp')
            unixt = lambda x: timegm(x.timetuple())+1e-6*x.microsecond
            iso = lambda x: x.isoformat(" ")
            times = ds.values_list('timestamp',flat=True)
            stamps = map(unixt,times)
            dates = map(iso,times)
            print datetime.now() - now
            return cals,normcals,list(sc),list(bg),dates,stamps,[int(i) for i in ids],cats
    return cals,normcals,[],[],dates,stamps,[],cats

def supercaldata(planet):
    calibs = []
    # assume data which has Decisions forms part of a complete set
    # People and their sources who have Dips in the select planet
    decs = Decision.objects.values_list('person','source').filter(value='D',current=True,planet__name=planet).annotate(Count('source'))
    numsuper = decs.count()
    # Create a lists of sources  and people
    if decs:
        people,sourcelst,tmp = zip(*decs)
        sources = set(sourcelst)
        for p in people:
            calslist = []
            vals = Datapoint.objects.filter(data__event__name=planet,user=p).order_by('data__timestamp')
            sourceave = vals.filter(pointtype='S').annotate(mean=Avg('value')).values_list('mean',flat=True)
            bgave = vals.filter(pointtype='B').annotate(mean=Avg('value')).values_list('mean',flat=True)
            # make into Numpy arrays for easier manipulation
            sc = array(sourceave)
            bg = array(bgave)
            calvals = Datapoint.objects.values('data','coorder__source').filter(user= p,coorder__source__in=sources,pointtype='C')
            for c in sources:
                calaves = calvals.filter(coorder__source=c)
                calpoints = calaves.order_by('data__timestamp').annotate(mean=Avg('value')).values_list('mean',flat=True)
                if calpoints.count() == planet.numobs:
                    calslist.append(list(calpoints))
            if calslist:
                calstack = vstack(calslist)
                # This throws a wobbly sometimes
                cc = (sc-bg)/(calstack-bg)
                calibs.append(cc.tolist())
        #superc = mean(cc,axis=0)
        try:
            cala = vstack(calibs)
            norm_a = lambda a: mean(r_[a[:3],a[-3:]])
            norms = apply_along_axis(norm_a, 1, cala)
            dim = len(cala)
            norm1 = cala/norms.reshape(dim,1)
        except:
            print "\033[1;35mHave you started again but not removed all the data?\033[1;m"
            return None,[],[],None
        norm_alt = mean(norm1,axis=0)
        variance = var(norm1,axis=0)
        std = sqrt(variance)
        # mean(r_[superc[:3],superc[-3:]])
        fz = list(norm_alt)
        if numsuper > 1:
            p = modelfit(fz,vals[0].data.target)
        else:
            p = 0.
        return numsuper,fz,list(std),p
    else:
        return None,[],[],None


def modelfit(fz,target):
    # t0 = ds[0].target.midpoint
    # data_z0 = sorted(ds, key=lambda dat: abs(dat-t0))
    # tmax = max(data_z0[:5])
    # tmin = min(data_z0[:5])
    mid = int(len(fz)/2.)
    fz0 = mean(fz[mid-2:mid+2])
    ap = target.ap 
    rx = target.rstar 
    i_r = deg2rad(target.inclination)
    # z0 = cos(i_r)**2.*(ap/(0.0046491*rx))**2.# convert Rsun to AU using the inclination
    z0 = (ap/(0.0046491*rx))**2. #not using the inclination
    z14 = 0.5*(1.+3.*z0**2.)**2.
    p = sqrt((4./5.*(1-fz0))/(1.-z0))
    return p

def leastmeasured(code):
    coords = []
    e = Event.objects.filter(name=code)[:1]
    dc = DataCollection.objects.values('source').filter(~Q(source=None),planet__name=code).annotate(count = Count('source')).order_by('count')[:4]
        # e = Event.objects.filter(name=code)
        # finderdp = Datapoint.objects.values_list('xpos','ypos').filter(user=person,data__id=e[0].finder,pointtype='C',coorder__calid__lt=3).order_by('coorder__calid')
        # finder = basiccoord - array(finderdp)
        # t = transpose(finder)
        # xmean = mean(t[0])
        # ymean = mean(t[1])
    for coll in dc:
        s = CatSource.objects.get(id=coll['source'])
        coords.append({'x':int(s.xpos),'y':int(s.ypos),'r':int(e[0].radius)})
    return coords   
        
def proxyconnect(request):
    if request.user.is_anonymous():
        user = ""
    else:
        try:
            name = request.user.get_full_name()
        except:
            name = "none given"
        user = "UniqueID=%s " % request.user.id
        user += "Name=%s " % name
        user += "Email=%s " % request.user.email
    return HttpResponse(user,mimetype='text/html')
def upload_dataset():
    #################
    # Unused function for making use of exisiting API for access RTI data
    request.POST.get()
    u1=urllib2.urlopen('http://ari-archive.lcogt.net/cgi-bin/oc_search?op-centre=LCO&user-id=avi.shporer&proposal-id=LCO2010A-051&group-id=WASP-24%20May29')
    dom = parse(u1)
    for elem in dom.getElementsByTagName('observation'):
        e = elem.getElementsByTagName('file-hfit')
        for node in e:
            node.firstChild.nodeValue

def update_web_pref(request,setting):
    #################
    # AJAX update user preference for web or  manual input of data
    if (request.user.is_authenticated()):
        person = request.user
    else:
        person = guestuser
    o = Observer.objects.filter(user=person)
    if setting == 'yes':
        o.update(dataexplorview=True)
        return HttpResponse("Setting changed to use web view")
    elif setting == 'no':
        o.update(dataexploreview = False)
        return HttpResponse("Setting changed to use manual view")
    else:
        return HttpResponse("Setting unchanged")
            
def tester(request):
    #measurement = Datapoint.objects.filter(taken=date,data__event__name=code)
    #calibrate(measurement)
    # code='corot2b'
    # if (request.user.is_authenticated()):
    #     o = Observer.objects.filter(user=request.user)
    # else:
    #     o = Observer.objects.filter(user=guestuser)
    # 
    # calibrators = []
    # cals = Datapoint.objects.values_list('data__timestamp').filter(data__event__name=code,pointtype = 'C').annotate(mean=Avg('value'))
    # #cals[0].data.target
    # for c in cals:
    #     datestamp = timegm(c[0].timetuple())+1e-6*c[0].microsecond
    #     data = (datestamp,c[1])
    #     calibrators.append(data)
    #return render_to_response('dataexplorer/test.html', {'event':Event.objects.filter(name=code)[0],'cal':simplejson.dumps(calibrators),'target':DataSource.objects.filter(event__name=code)[0].target}, context_instance=RequestContext(request))
    if (request.POST):
        fitsanalyse(request)
    else:
        return render_to_response('dataexplorer/test_local.html')
    
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
        print "Reduced %s" % date
        
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
def personcheck(request):
    if (request.user.is_authenticated()):
        o = Observer.objects.filter(user=request.user)
    else:
        o = Observer.objects.filter(user__id=guestuser)
    return o[0]
    
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