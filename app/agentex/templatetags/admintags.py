from django.template import Template, Library
from django.contrib.admin.models import LogEntry, ADDITION
from datetime import date, datetime, timedelta
import time

from agentex.models import Event, Datapoint, DataSource, DataCollection,CatSource, Decision, Achievement, Badge, User

register = Library()

@register.inclusion_tag('agentex/agentex_info.html')
def agentex_info():
    planets = Event.objects.filter(enabled=True)
    cols = DataCollection.objects.filter(complete=True)
    completes =[]
    for p in planets:
        name = p.title
        num = cols.filter(planet=p).count()
        completes.append({'name':name,'subtotal':num,'id':p.id})
    volunteers = User.objects.all()
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

@register.inclusion_tag('agentex/get_last_login.html')
@register.filter(expects_localtime=True)  #Allows Django to use local time
def get_last_login():

    #Empty list to store users
    users = []

    #Gets the last 10 users to have signed in
    last = User.objects.all().order_by('-last_login')[:10]

    #Loops through last 10 users and appends their usernames
    for i in last:
        username = i.username
        login_date = i.last_login
        users.append({'user': username, 'lastlogin': login_date})

    ###################################

    #Finds the number of users logged in within 7 days
    week_users = User.objects.filter(last_login__gte=date.today()-timedelta(7)).count()

    return {'users':users, 'num_users':week_users}
