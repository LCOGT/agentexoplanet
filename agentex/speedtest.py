from datetime import datetime,timedelta
import MySQLdb
from citsciportal.settings import DATABASES as dbc
from django.db import connection

from django.db.models import Count,Avg,Min,Max,Variance, Q, Sum
from citsciportal.agentex.models import Target, Event, Datapoint, DataSource, CatSource, Decision, DataCollection

def averages(code,person):
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
    dcall = DataCollection.objects.filter(planet=e,source__in=cs).values_list('id',flat=True)
    # print "** Collections %s" % dcall.count()
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
            ds = DataSource.objects.filter(event__name=code,id__in=ids).order_by('timestamp')
            mysource = ds.filter(datapoint__pointtype='S',datapoint__user=person).annotate(value=Sum('datapoint__value')).values_list('id','value')
            mybackgs = ds.filter(datapoint__pointtype='B',datapoint__user=person).annotate(value=Sum('datapoint__value')).values('id','value')
            
            sc_ave = fetch_averages_sql(code,'S')
            bg_ave = fetch_averages_sql(code,'B')
            # Combine my values with the average
            sources =  dict(sc_ave.items() + sc_my.items())
            sources =  dict(bg_ave.items() + bg_my.items())
            



def calibratorpage(code,person):
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
    dcall = DataCollection.objects.filter(planet=e,source__in=cs).values_list('id',flat=True)
    # print "** Collections %s" % dcall.count()
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
            ds = DataSource.objects.filter(event__name=code,id__in=ids).order_by('timestamp')
            #points = Datapoint.objects.filter(data__id__in=ids)
            #dps = Datapoint.objects.filter(coorder__in=dcall).values_list('taken','user','data')
            #taken,users,data = zip(*dps)
            users = DataCollection.objects.filter(id__in=dcall).values_list('person',flat=True).distinct()
            print users
            print datetime.now() - now
            # points = Datapoint.objects.filter(taken__in=taken,user__in=users,data__event__name=code).order_by('data__timestamp')
            points = Datapoint.objects.filter(user__in=users,data__event__name=code).order_by('data__timestamp')
            print datetime.now() - now
            scA = points.filter(pointtype='S').values_list('data__id').annotate(ave=Avg('value'))
            #scA = points.filter(pointtype='S',id__in=points).order_by('data__timestamp').values_list('data__id').annotate(Avg('value'))
            bgA = points.filter(pointtype='B').values_list('data__id').annotate(Avg('value'))
            tmp,sc=zip(*scA)
            tmp,bg=zip(*bgA)
            print "Datapoint unzip"
            print datetime.now() - now
            now2 = datetime.now()
            mypoints = Datapoint.objects.filter(user = person,data__event__name=code)
            print "My points using Code %s" % mypoints.filter(pointtype='S').count()
            print datetime.now() - now2
            mypoints = Datapoint.objects.filter(pointtype='S',data__id__in=ids,user=person).order_by('data__timestamp')
            print "My points using IDs %s" % mypoints.filter(pointtype='S').count()
            print datetime.now() - now2
            # Find my data and create unix timestamps
            mydp = DataSource.objects.filter(event__name=code).order_by('timestamp')
            mysource = ds.filter(datapoint__pointtype='S',datapoint__user=person).annotate(value=Sum('datapoint__value')).values_list('id','value')
            mybackgs = ds.filter(datapoint__pointtype='B',datapoint__user=person).annotate(value=Sum('datapoint__value')).values('id','value')
            print datetime.now() - now2
            print "DataSource look up %s" % source.count()
            print "lists"
            sc_my = dict(source)
            b = dict(scA)
            print datetime.now() - now2
            sc_sql = fetch_averages_sql(code,'S')
            print datetime.now() - now2
            #print set(sc_sql) - set(a)
            print sc_sql, len(sc_sql)
            print "***"
            print sc_my, len(sc_my)
            print "***"
            print dict(sc_sql.items() + sc_my.items())
            sources = Datapoint.objects.values_list('value',flat=True).filter(pointtype='S',data__id__in=ids,user=person).order_by('data__timestamp')
            backgs = Datapoint.objects.values_list('value',flat=True).filter(pointtype='B',data__id__in=ids,user=person).order_by('data__timestamp')
            lookup = Datapoint.objects.values_list('data__id', flat=True).filter(pointtype='S',data__event=e,user=person).order_by('data__timestamp')
            mypoints = Datapoint.objects.filter(pointtype='C',data__id__in=ids,user=person).order_by('data__timestamp')
            print datetime.now() - now2
            print "Datapoint lookup %s" % sources.count()
            print datetime.now() - now2
            
def fetch_averages_sql(code,pointtype):
    # now = datetime.now()
    # print datetime.now() - now
    ds = DataSource.objects.filter(event__name=code)
    maxnum = ds.count()
    db = MySQLdb.connect(user=dbc['default']['USER'], passwd=dbc['default']['PASSWORD'], db=dbc['default']['NAME'], host=dbc['default']['HOST'])
    # Match supplied user name to one in Drupal database
    sql = "SELECT dp.data_id, avg(dp.value) FROM dataexplorer_datapoint AS dp, dataexplorer_datasource AS ds WHERE dp.data_id = ds.id and dp.pointtype = '%s' AND dp.data_id BETWEEN %s AND %s GROUP BY dp.data_id, coorder_id order by ds.timestamp" % (pointtype,ds[0].id,ds[maxnum-1].id)
    sources = db.cursor()
    sources.execute(sql)
    ave_values = dict(sources.fetchall())
    # print datetime.now() - now
    db.close()
    return ave_values
    
def fetch_averages_raw(code,pointtype):
    cursor = connection.cursor()
    ds = DataSource.objects.filter(event__name=code)
    maxnum = ds.count()
    params = [pointtype,ds[0].id,ds[maxnum-1].id]
    cursor.execute('SELECT dp.data_id, avg(dp.value) FROM dataexplorer_datapoint AS dp, dataexplorer_datasource AS ds WHERE dp.data_id = ds.id and dp.pointtype = %s AND dp.data_id BETWEEN %s AND %s GROUP BY dp.data_id, coorder_id order by ds.timestamp', params)
    ave_values = dict(cursor.fetchall())
    return ave_values
            
# select dp.data_id, dp.coorder_id, avg(dp.value), count(dp.value) from dataexplorer_datapoint as dp, dataexplorer_datasource as ds where dp.data_id = ds.id and dp.pointtype = 'C' and dp.data_id >= 976 and dp.data_id <= 1105 and user_id = 11 group by dp.data_id, coorder_id