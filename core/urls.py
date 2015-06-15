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
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model
from django.conf import settings
from django.contrib.auth.models import User, check_password
from django.contrib.auth.backends import ModelBackend
import MySQLdb
import hashlib
from settings import DATABASES as dbc
from agentex.models import Observer

        
def matchRTIPass(username,password):
    # Retreive the database user information from the settings
    db = MySQLdb.connect(user=dbc['wis']['USER'], passwd=dbc['wis']['PASSWORD'], db=dbc['wis']['NAME'], host=dbc['wis']['HOST'])

    # Match supplied user name to one in Drupal database
    sql_users = "SELECT schoolloginname, password, contactemailaddress,tag,schoolname FROM registrations WHERE schoolloginname='%s' AND (accountstatus = 'active' OR accountstatus = 'suspended')" % username
    rti = db.cursor()
    rti.execute(sql_users)
    user = rti.fetchone()
    rti.close()
    db.close()
    if user:
        if (password == user[1]):
            ###### If the user does not have an email address return false
            if user[2]:
                return user[2], user[3], user[4]
            else:
                return False
    else:
        return False
        
def checkUserObject(params,username,password):
    email = params[0]
    tag = params[1]
    org = params[2]
    try:
        user = User.objects.get(username=username)
        hashpass = hashlib.md5(password).hexdigest()
        if (user.password != hashpass):
            user.password = hashpass
            user.save()
    except User.DoesNotExist:
        name_count = User.objects.filter(username__startswith = username).count()
        if name_count:
            username = '%s%s' % (username, name_count + 1)
            user = User.objects.create_user(username,password=password,email=email)
        else:
            user = User.objects.create_user(username,password=password,email=email)
#### Check there is an observer for this user
    try:
        o = Observer.objects.get(user=user)
    except:
        if tag and org:
            o = Observer(user=user,tag=tag,organization=org)
        elif tag:
            o = Observer(user=user,tag=tag)
        else:
            o = Observer(user=user)
        o.save()
    return user   
         
class LCOAuthBackend(ModelBackend):         
    def authenticate(self, username=None, password=None):
        fns =  matchRTIPass(username, password)
        for response in fns:
            if (response):
                return checkUserObject(response,username,password)
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None  

            
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
DATA_LOCATION ='/Volumes/Tardis-type40/AgentExoplanetData/agentexdata'
DATA_URL = 'http://127.0.0.1/agentexdata'

PREFIX = ''
DEBUG = True
PRODUCTION = False
STATIC_ROOT =  '/Users/egomez/Sites/static'
STATIC_URL = '/static/'

LOGIN_URL = 'http://localhost:8000/account/login/'
LOGIN_REDIRECT_URL = '/''''
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
# Django settings for observing project.

import os
import platform
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from django.utils.crypto import get_random_string


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
LOCAL_DEVELOPMENT = False if CURRENT_PATH.startswith('/var/www') else True
PRODUCTION = True

DEBUG = False

PREFIX ="/agentexoplanet"
BASE_DIR = os.path.dirname(CURRENT_PATH)

ADMINS = (
     ('Edward Gomez', 'egomez@lcogt.net'),
)

MANAGERS = ADMINS

DATABASES = {
 'default' : {
    'NAME'      : 'citsciportal',
    "USER": os.environ.get('CITSCI_DB_USER',''),
    "PASSWORD": os.environ.get('CITSCI_DB_PASSWD',''),
    "HOST": os.environ.get('CITSCI_DB_HOST',''),
    "OPTIONS"   : {'init_command': 'SET storage_engine=INNODB'},
}
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True


MEDIA_ROOT = '/var/www/html/media/'
MEDIA_URL = '/media/'

STATIC_ROOT = '/var/www/html/static/'
STATIC_URL = PREFIX + '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'agentex'),os.path.join(BASE_DIR,'showmestars')]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
 )

# Make this unique, and don't share it with anybody.
chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
SECRET_KEY = get_random_string(50, chars)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)  

CACHE_MIDDLEWARE_SECONDS = '1'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    )

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'agentex',
    'showmestars',
    'core'
)

LOGIN_REDIRECT_URL = 'http://lcogt.net/agentexoplanet/'
LOGIN_URL = 'http://lcogt.net/agentexoplanet/account/login/'

BASE_URL = "/agentexoplanet/"

DATA_LOCATION = CURRENT_PATH + '/media/data'
DATA_URL = '/agentexoplanet/media/data'

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
if LOCAL_DEVELOPMENT:
    try:
        from local_settings import *
    except ImportError as e:
        if "local_settings" not in str(e):
            raise e
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
