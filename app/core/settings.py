'''
Citizen Science Portal: App containing Agent Exoplant for Las Cumbres Observatory Global Telescope Network
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
# Django settings for Agent Exoplanet

import os
import platform
from django.utils.crypto import get_random_string
from django.conf import settings


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
PRODUCTION = True if CURRENT_PATH.startswith('/var/www') else False
LOCAL_DEVELOPMENT = not PRODUCTION

DEBUG = not PRODUCTION

PREFIX = os.environ.get('PREFIX', '/agentexoplanet')
FORCE_SCRIPT_NAME = PREFIX
BASE_DIR = os.path.dirname(CURRENT_PATH)

ADMINS = (
)

MANAGERS = ADMINS

DATABASES = {
 'default' : {
    'ENGINE'    : 'django.db.backends.mysql',
    # 'ENGINE'    : 'django.db.backends.sqlite3',
    'NAME'      : os.environ.get('CITSCI_DB_NAME',''),
    "USER"      : os.environ.get('CITSCI_DB_USER',''),
    "PASSWORD"  : os.environ.get('CITSCI_DB_PASSWD',''),
    "HOST"      : os.environ.get('CITSCI_DB_HOST',''),
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
MEDIA_URL = PREFIX + '/media/'

DATA_LOCATION = MEDIA_ROOT + '/data'
DATA_URL = MEDIA_URL + 'data'

STATIC_ROOT = '/var/www/html/static/'
STATIC_URL = PREFIX + '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'agentex','static')]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
 )

SECRET_KEY = os.environ.get('SECRET_KEY','')
if not SECRET_KEY:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    SECRET_KEY = get_random_string(50, chars)

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Added by TJ to allow static files declaration
    # 'debug_toolbar',
    'agentex.apps.AgentConfig',
    'opbeat.contrib.django',
)

OPBEAT = {
    'ORGANIZATION_ID': os.environ.get('OPBEAT_ORGID',''),
    'APP_ID': os.environ.get('OPBEAT_APPID',''),
    'SECRET_TOKEN': os.environ.get('OPBEAT_TOKEN',''),
}


LOGIN_REDIRECT_URL = 'https://lco.global/agentexoplanet/'
LOGIN_URL = 'https://lco.global/agentexoplanet/account/login/'


SESSION_COOKIE_DOMAIN='lco.global'
SESSION_COOKIE_NAME='agentexoplanet.sessionid'


BASE_URL = "/agentexoplanet/"

EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS       = True
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_HOST_USER     = os.environ.get('EMAIL_USERNAME','')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD','')
EMAIL_PORT          =  587
DEFAULT_FROM_EMAIL  = 'Agent Exoplanet <agentexoplanet@lco.global>'
EMAIL_REPLYTO       = 'agentexoplanet@lco.global'

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ['127.0.0.1']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        },
        'core' : {
            'handlers' : ['console'],
            'level'    : 'DEBUG',
        },
        'agentex' : {
            'handlers' : ['console'],
            'level'    : 'DEBUG',
        }
    }
}

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
if not PRODUCTION:
    try:
        from local_settings import *
    except ImportError as e:
        if "local_settings" not in str(e):
            raise e
