from django.template import RequestContext, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
import MySQLdb
from citsciportal.settings import DATABASES as dbc
from datetime import datetime

from datetime import datetime
import time

events = [
    {
        'guestid'   : '4661',
        'name'      : 'Mark Thompson',
        'current'   : True,
        'slots'     : [79386,79387],
        'start'     :datetime(2011,8,19,13,0),
        'end'       :datetime(2011,8,19,14,0),
        'site'      : 'ogg',
    },
    {
        'guestid'   : '56',
        'name'      : 'Dara O Briain',
        'current'   : False,
        'slots'     : [79286,79287],
        'start'     : datetime(2011,8,9,12,0),
        'end'       : datetime(2011,8,9,13,0),
        'site'      : 'ogg',
    },
    # {
    #     'guestid'   : '',
    #     'name'      : 'Mark Thompson',
    #     'current'   : True,
    #     'slots'     : [6,7],
    #     'start'     : datetime(2011,8,19,13,0),
    #     'end'       : datetime(2011,8,19,14,0),
    #     'site'      : 'coj',
    # },
]
    
def latestimages(request,eventid):
    try:
        eid = int(eventid)
    except ValueError:
        raise Http404
    try:
        event = events[eid]
    except:
        raise Http404
          
    userid = event['guestid']
    newevents = []
# Start connection
    db = MySQLdb.connect(user=dbc['faulkes']['USER'], passwd=dbc['faulkes']['PASSWORD'], db=dbc['faulkes']['NAME'], host=dbc['faulkes']['HOST'])
    for e in events:
        # Find new observations
        sql_images = "SELECT ImageID, WhenTaken,Filename,TelescopeId,SkyObjectName,filter FROM imagearchive WHERE  SchoolID ='%s' AND WhenTaken > '%s' AND WhenTaken < '%s' order by WhenTaken desc;" % (e['guestid'], e['start'].strftime("%Y%m%d%H%M%S"), e['end'].strftime("%Y%m%d%H%M%S"))
        images = db.cursor()
        images.execute(sql_images)
        obs = []
        for i in images:
            obs.append(makeimagebox(i))
        e['obs'] = obs
        newevents.append(e)
    stamp = datetime.utcnow()
    db.close()
    return render_to_response('imageportal.html',{'stamp':stamp,'event':newevents}, context_instance=RequestContext(request))
    
def newimage(request,eventid):
    try:
        eid = int(eventid)
    except ValueError:
        raise Http404
    userid = events[eid]['guestid']
    obs = []
    stamp = request.POST.get('stamp','0')
    db = MySQLdb.connect(user=dbc['faulkes']['USER'], passwd=dbc['faulkes']['PASSWORD'], db=dbc['faulkes']['NAME'], host=dbc['faulkes']['HOST'])
    sql_images = "SELECT ImageID, WhenTaken,Filename,TelescopeId,SkyObjectName,filter FROM imagearchive  WHERE  SchoolID ='%s' AND WhenTaken > '%s' order by WhenTaken desc limit 20" % (userid,stamp)
    images = db.cursor()
    images.execute(sql_images)
    stamp = datetime.utcnow()
    for i in images:
        obs.append(makeimagebox(i))
    return render_to_response('imagebox.html',{'obs':obs,'stamp':stamp}, context_instance=RequestContext(request))


def makeimagebox(image):
    telescopeont = ('ogg/2m0a','coj/2m0a')
    telescope = ('Faulkes Telescope North','Faulkes Telescope South')
    WhenTaken = image[1]
    taken = datetime(*time.strptime(WhenTaken , "%Y%m%d%H%M%S")[0:5])
    #d = "%s" % s.strftime("%a, %d %b %Y")
    filename = image[2]
    try:
        filter = ""
    except:
        filter = "Unknown"
    faulkes_url = "http://rti.faulkes-telescope.com/"
    image_url = "observations/%s/%s/%s/%s" % (WhenTaken[:4],WhenTaken[4:6],WhenTaken[6:8],filename[:-4])
    fullimage_url = "%s%s-%s_150.jpg" % (faulkes_url,image_url,image[3])
    smallimage_url = "%s%s-%s_120.jpg" % (faulkes_url,image_url,image[3])
    urlobs = "http://lcogt.net/observations/%s/%s" % (telescopeont[image[3]-1],image[0])
    obs = {'id'         : image[0],
            'telescope' : telescope[image[3]-1],
            'filter'    : filter,
            'date'      : taken.strftime("%a, %d %b %Y"),
            'imageurl'  : fullimage_url,
            'obsurl'    : urlobs,
            'name'      : image[4],
            'stamp'     : WhenTaken,
    }
    return obs