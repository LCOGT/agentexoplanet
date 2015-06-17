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
# Django settings for observing project.

import os
import platform
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from django.utils.crypto import get_random_string
from django.conf import settings


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
LOCAL_DEVELOPMENT = False if CURRENT_PATH.startswith('/var/www') else True
PRODUCTION = True

DEBUG = True

PREFIX ="/agentexoplanet"
BASE_DIR = os.path.dirname(CURRENT_PATH)

ADMINS = (
     ('Edward Gomez', 'egomez@lcogt.net'),
)

MANAGERS = ADMINS

DATABASES = {
 'default' : {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME'      : os.environ.get('CITSCI_DB_NAME',''),
    "USER": os.environ.get('CITSCI_DB_USER',''),
    "PASSWORD": os.environ.get('CITSCI_DB_PASSWD',''),
    "HOST": os.environ.get('CITSCI_DB_HOST',''),
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


#MEDIA_ROOT = '/var/www/html/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
MEDIA_URL = '/media/'

#STATIC_ROOT = '/var/www/html/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_URL = '/static/'
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
                'django.core.context_processors.static', # Serves static files (added by TJ)
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
    'django.contrib.staticfiles', # Added by TJ to allow static files declaration
    'agentex',
    'showmestars',
    'core',
)

LOGIN_REDIRECT_URL = 'http://lcogt.net/agentexoplanet/'
LOGIN_URL = 'http://lcogt.net/agentexoplanet/account/login/'

BASE_URL = "/agentexoplanet/"

DATA_LOCATION = CURRENT_PATH + '/media/data'
DATA_URL = '/agentexoplanet/media/data'

ALLOWED_HOSTS = ['*']

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
