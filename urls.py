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
    (r'^account/login/$', login, {'template_name' :'login.html'}),
    (r'^account/logout/$', logout,{'template_name' :'logout.html'}),
    url(r'^account/register/$', 'agentex.views.register',name='register'),
    (r'^account/$', 'agentex.views.editaccount'),
    (r'^account/profile/agentex/$','agentex.views.profile'),
    ('^agentex/',redirect_to, {'url':'/agentexoplanet/'}),
    (r'^agentexoplanet/',include('agentex.urls')),
    (r'^showmestars/newimage/$','showmestars.views.newimage',{'eventid':0}),
    (r'^showmestars/(?P<eventid>\w+)/$','showmestars.views.latestimages'),
    (r'^showmestars/$','showmestars.views.latestimages',{'eventid':0}),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.LOCAL_DEVELOPMENT:
    urlpatterns += patterns("django.views",
        url(r"%s(?P<path>.*)/$" % settings.MEDIA_URL[1:], "static.serve", {
            "document_root": settings.MEDIA_ROOT,
        })
    )
