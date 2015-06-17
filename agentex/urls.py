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
from django.conf.urls import include, url
from django.contrib.auth.views import login, logout
from .views import *

from django.conf import settings

urlpatterns = [
    url(r'^$',index, name='index'),
    url(r'^account/login/$', login, {'template_name' :'login.html'}, name='login'),
    url(r'^account/logout/$', logout,{'template_name' :'logout.html'}, name='logout'),
    url(r'^account/register/$', register, name='register'),
    url(r'^account/$', editaccount, name='editaccount'),
    url(r'^profile/$',profile, name='profile'),
    url(r'^planets/$',target, name='target'),
    url(r'^fitsanalyse',fitsanalyse, name='fitsanalyse'),
    url(r'^test',tester, name='tester'),
    url(r'^briefing/read/$',read_manual_check, name='read_manual_check'),
    url(r'^briefing/$',briefing, name='briefing'),
    url(r'^comment/$',addcomment, name='addcomment'),
    url(r'^(?P<code>\w+)/view/$',addvalue, name='addvalue'),
    url(r'^(?P<code>\w+)/graph/update/$',updatedataset, name='updatedataset'),
    url(r'^(?P<code>\w+)/lightcurve/advanced/$',graphview, {'mode' : 'advanced','calid':None}, name='advanced-graph'),
    url(r'^(?P<code>\w+)/lightcurve/me/$',graphview, {'mode' : 'simple','calid':None}, name='my-graph'),
    url(r'^(?P<code>\w+)/lightcurve/calibrator/update/$',classifyupdate, name='classifyupdate'),
    url(r'^(?P<code>\w+)/lightcurve/calibrator/$',graphview, {'mode' : 'ave','calid':None}, name='average-graph'),
    url(r'^(?P<code>\w+)/lightcurve/calibrator/(?P<calid>\w+)/$',graphview, {'mode' : 'ave'}, name='calibrator-graph'),
    url(r'^(?P<code>\w+)/lightcurve/$',graphsuper,name='super-graph'),
    url(r'^(?P<code>\w+)/$',infoview, name='infoview'),
    url(r'^(?P<code>\w+)/data.(?P<format>\w+)',measurementsummary, name='measurementsummary'),
]