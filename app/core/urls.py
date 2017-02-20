from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles import views

from agentex.admin import calibrator_check, allcalibrators_check
from agentex.views import index, register, editaccount, profile, target, fitsanalyse, read_manual_check, briefing, addcomment, addvalue, updatedataset, graphview, classifyupdate, graphview, graphsuper, infoview, measurementsummary

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls), name='agentexo_admin'),
    url(r'^account/login/$', login, {'template_name': 'agentex/login.html'}, name='login'),
    url(r'^account/logout/$', logout, {'template_name': 'agentex/logout.html'}, name='logout'),

    url(r'^admin/calibrators/(?P<planetid>\d+)/id/(?P<calid>\d+)/$',calibrator_check, name='agentex_admin_calib'),
    url(r'^admin/calibrators/(?P<planetid>\d+)/$',allcalibrators_check, name='agentex_all_calib'),
    url(r'^$',index, name='index'),
    url(r'^account/register/$', register, name='register'),
    url(r'^account/$', editaccount, name='editaccount'),
    url(r'^profile/$',profile, name='profile'),
    url(r'^planets/$',target, name='target'),
    url(r'^fitsanalyse',fitsanalyse, name='fitsanalyse'),
    #url(r'^test',tester, name='tester'),
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

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]
