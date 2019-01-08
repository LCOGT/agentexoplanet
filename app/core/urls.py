from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.staticfiles import views
from django.urls import include, path

from agentex.admin import calibrator_check, allcalibrators_check
from agentex.views import index, AddValuesView, \
    read_manual_check, updatedataset, graphview_simple, graphview_advanced, \
    classifyupdate, graphview_ave, graphsuper, measurementsummary, \
    EventView, EventList, DataEntry, next_datasource
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
    path('fitsanalyse/',AddValuesView.as_view(), name='fitsanalyse'),
    #path('test',tester, name='tester'),
    path('briefing/read/',read_manual_check, name='read_manual_check'),
    path('briefing/',briefing, name='briefing'),
    path('comment/',feedback, name='addcomment'),
    path('source/<int:pk>/view/',DataEntry.as_view(), name='addvalue'),
    path('target/<slug:slug>/next/', next_datasource, name='next_addvalue'),
    path('target/<slug:slug>/graph/update/',updatedataset, name='updatedataset'),
    path('target/<slug:slug>/lightcurve/advanced/',graphview_advanced, name='advanced-graph'),
    path('target/<slug:slug>/lightcurve/me/',graphview_simple, name='my-graph'),
    path('target/<slug:slug>/lightcurve/calibrator/update/',classifyupdate, name='classifyupdate'),
    path('target/<slug:slug>/lightcurve/calibrator/',graphview_ave, name='average-graph'),
    path('target/<slug:slug>/lightcurve/calibrator/<int:calid>/',graphview_ave, name='calibrator-graph'),
    path('target/<slug:slug>/lightcurve/',graphsuper,name='super-graph'),
    path('target/<slug:slug>/',EventView.as_view(), name='infoview'),
    path('target/<slug:slug>/data.<str:format>',measurementsummary, name='measurementsummary'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
