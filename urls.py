from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.views.generic.simple import redirect_to


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
#    (r'^api/', include('odin.api.urls')),
    url(r'^$','citsciportal.agentex.views.home',name='portal'),
    (r'^auth$','citsciportal.agentex.views.proxyconnect'),
    (r'^account/login/$', login, {'template_name' :'login.html'}),
    (r'^account/logout/$', logout,{'template_name' :'logout.html'}),
    url(r'^account/register/$', 'citsciportal.agentex.views.register',name='register'),
    (r'^account/$', 'citsciportal.agentex.views.editaccount'),
    (r'^account/profile/agentex/$','citsciportal.agentex.views.profile'),
    ('^agentex/',redirect_to, {'url':'/agentexoplanet/'}),
    (r'^agentexoplanet/',include('citsciportal.agentex.urls')),
    (r'^showmestars/newimage/$','citsciportal.showmestars.views.newimage',{'eventid':0}),
    (r'^showmestars/(?P<eventid>\w+)/$','citsciportal.showmestars.views.latestimages'),
    (r'^showmestars/$','citsciportal.showmestars.views.latestimages',{'eventid':0}),
    (r'^admin/', include(admin.site.urls)),
)

if settings.LOCAL_DEVELOPMENT:
    urlpatterns += patterns("django.views",
        url(r"%s(?P<path>.*)/$" % settings.MEDIA_URL[1:], "static.serve", {
            "document_root": settings.MEDIA_ROOT,
        })
    )
