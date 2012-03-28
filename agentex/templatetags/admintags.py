from django.template import Template, Library
from django.contrib.admin.models import LogEntry, ADDITION
from datetime import date, datetime, timedelta
import time

from citsciportal.agentex.models import Target, Event, Datapoint, DataSource, DataCollection,CatSource, Decision, Achievement, Badge, Observer

register = Library()

@register.inclusion_tag('agentex/agentex_info.html')
def agentex_info():
    planets = Event.objects.filter(enabled=True)
    cols = DataCollection.objects.filter(complete=True)
    completes =[]
    for p in planets:
        name = p.title
        num = cols.filter(planet=p).count()
        completes.append({'name':name,'subtotal':num})
    volunteers = Observer.objects.all()
    readmanual = Achievement.objects.filter(badge__name='manual').count()
    params = { 'planets' : planets.count(),
               'completes'  : {'total': cols.count(),
                                'planets': completes},
               'web_users': volunteers.filter(user__first_name=False).count(),
               'total_users' :  volunteers.count(),
               'readmanual': readmanual,
               }
    return params

@register.inclusion_tag('admin/commentslist.html')
def commentslist():
    logs = LogEntry.objects.filter(action_flag=ADDITION,content_type__id=3).order_by('-action_time')[:20]
    return {'logs' : logs}