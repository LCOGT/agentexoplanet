from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.staticfiles import views
from django.urls import include, path

from agentex.admin import calibrator_check, allcalibrators_check
from agentex.views import index, target, fitsanalyse, \
    read_manual_check, addvalue, updatedataset, graphview, \
    classifyupdate, graphview, graphsuper, infoview, measurementsummary, \
    EventView, EventList
from agentex.users import register, editaccount, profile, briefing, feedback

admin.autodiscover()

urlpatterns = [
    path('',index, name='index'),
    path('admin/', admin.site.urls),
    path('account/login/', LoginView.as_view(template_name= 'agentex/login.html'), name='login'),
    path('account/logout/', LogoutView.as_view(template_name='agentex/logout.html'), name='logout'),

    path('admin/calibrators/<int:planetid>/id/<int:calid>/',calibrator_check, name='agentex_admin_calib'),
    path('admin/calibrators/<int:planetid>/',allcalibrators_check, name='agentex_all_calib'),
    path('account/register/', register, name='register'),
    path('account/', editaccount, name='editaccount'),
    path('profile/',profile, name='profile'),
    path('planets/',EventList.as_view(), name='target'),
    path('fitsanalyse/',fitsanalyse, name='fitsanalyse'),
    #path('test',tester, name='tester'),
    path('briefing/read/',read_manual_check, name='read_manual_check'),
    path('briefing/',briefing, name='briefing'),
    path('comment/',feedback, name='addcomment'),
    path('target/<slug:code>/view/',addvalue, name='addvalue'),
    path('target/<slug:code>/view/',addvalue, name='addvalue'),
    path('target/<slug:code>/graph/update/',updatedataset, name='updatedataset'),
    path('target/<slug:code>/lightcurve/advanced/',graphview, {'mode' : 'advanced','calid':None}, name='advanced-graph'),
    path('target/<slug:code>/lightcurve/me/',graphview, {'mode' : 'simple','calid':None}, name='my-graph'),
    path('target/<slug:code>/lightcurve/calibrator/update/',classifyupdate, name='classifyupdate'),
    path('target/<slug:code>/lightcurve/calibrator/',graphview, {'mode' : 'ave','calid':None}, name='average-graph'),
    path('target/<slug:code>/lightcurve/calibrator/<int:calid>/',graphview, {'mode' : 'ave'}, name='calibrator-graph'),
    path('target/<slug:code>/lightcurve/',graphsuper,name='super-graph'),
    path('target/<slug:code>/',EventView.as_view(), name='infoview'),
    path('target/<slug:code>/data.<str:format>',measurementsummary, name='measurementsummary'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
