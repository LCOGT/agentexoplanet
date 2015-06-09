from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.views.generic.simple import redirect_to


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
#    (r'^api/', include('odin.api.urls')),
    url(r'^$','agentex.views.home',name='portal'),
    #(r'^auth$','agentex.views.proxyconnect'),
    (r'^agentexoplanet/account/login/$', login, {'template_name' :'login.html'}),
    (r'^agentexoplanet/account/logout/$', logout,{'template_name' :'logout.html'}),
    url(r'^agentexoplanet/account/register/$', 'agentex.views.register',name='register'),
    (r'^agentexoplanet/account/$', 'agentex.views.editaccount'),
    (r'^agentexoplanet/account/profile/agentex/$','agentex.views.profile'),
    ('^agentexoplanet/agentex/',redirect_to, {'url':'/agentexoplanet/'}),
    (r'^agentexoplanet/admin/agentex/event/(?P<planetid>\d+)/calibrators/(?P<calid>\d+)/$','agentex.admin.calibrator_check'),
    (r'^agentexoplanet/admin/agentex/event/(?P<planetid>\d+)/calibrators/$','agentex.admin.allcalibrators_check'),
    (r'^agentexoplanet/admin/', include(admin.site.urls)),
    (r'^agentexoplanet/',include('agentex.urls')),
    (r'^showmestars/newimage/$','showmestars.views.newimage',{'eventid':0}),
    (r'^showmestars/(?P<eventid>\w+)/$','showmestars.views.latestimages'),
    (r'^showmestars/$','showmestars.views.latestimages',{'eventid':0}),
    (r'^agentexoplanet/comments/', include('django.contrib.comments.urls')),
)

if settings.LOCAL_DEVELOPMENT:
    urlpatterns += patterns("django.views",
        url(r"%s(?P<path>.*)/$" % settings.STATIC_URL[1:], "static.serve", {
            "document_root": settings.MEDIA_ROOT,
        })
    )
