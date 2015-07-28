from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles import views
from django.views.generic import RedirectView
from django.contrib.auth.views import login, logout

from agentex import urls
from agentex.views import home
from agentex.admin import calibrator_check, allcalibrators_check
#from admin.site import urls

#from showmestars.views import newimage, latestimages

admin.autodiscover()

urlpatterns = [
#    (r'^api/', include('odin.api.urls')),
    url(r'^home/$', home, name='portal'),
    url(r'^grappelli/', include('grappelli.urls'), name='agentexo_admin_grapp'), # grappelli urls
    url(r'^agentexoplanet/admin/', include(admin.site.urls), name='agentexo_admin'),
    url(r'^agentexoplanet/agentex/', RedirectView.as_view(url='/agentexoplanet/'), name='agentex_redirect'),
    url(r'^agentexoplanet/admin/calibrators/(?P<planetid>\d+)/id/(?P<calid>\d+)/$',calibrator_check, name='agentex_admin_calib'),
    url(r'^agentexoplanet/admin/calibrators/(?P<planetid>\d+)/$',allcalibrators_check, name='agentex_all_calib'),
    url(r'^agentexoplanet/',include(urls), name='agentexo_urls'),
#    url(r'^showmestars/newimage/$', newimage, {'eventid':0}, name='showmestars_newimage'),
#    url(r'^showmestars/(?P<eventid>\w+)/$', latestimages, name='showmestars_latestimage'),
#    url(r'^showmestars/$', latestimages, {'eventid':0}, name='showmestars_latestimage_event'),
 #   url(r'^login/$',login, name='site_login'),
  #  url(r'^logout/$',logout, name='site_logout'),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]