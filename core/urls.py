from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles import views
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = [
#    (r'^api/', include('odin.api.urls')),
    url(r'^$','agentex.views.home',name='portal'),
    url(r'^agentexoplanet/agentex/', RedirectView.as_view(url='/agentexoplanet/', name=''),
    url(r'^agentexoplanet/admin/agentex/event/(?P<planetid>\d+)/calibrators/(?P<calid>\d+)/$','agentex.admin.calibrator_check', name=''),
    url(r'^agentexoplanet/admin/agentex/event/(?P<planetid>\d+)/calibrators/$','agentex.admin.allcalibrators_check', name=''),
    url(r'^agentexoplanet/admin/', include(admin.site.urls), name=''),
    url(r'^agentexoplanet/',include('agentex.urls'), name=''),
    url(r'^showmestars/newimage/$','showmestars.views.newimage',{'eventid':0}, name=''),
    url(r'^showmestars/(?P<eventid>\w+)/$','showmestars.views.latestimages', name=''),
    url(r'^showmestars/$','showmestars.views.latestimages',{'eventid':0}, name='')
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]
