'''
Agent Exoplanet: Las Cumbres Observatory Global Telescope Network
Copyright (C) 2014-2019 LCOGT

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

from django.utils.crypto import get_random_string
from django.conf import settings

import ast
import os

def str2bool(value):
    '''Convert a string value to a boolean'''
    value = value.lower()

    if value in ('t', 'true', 'y', 'yes', '1', ):
        return True

    if value in ('f', 'false', 'n', 'no', '0', ):
        return False

    raise RuntimeError('Unable to parse {} as a boolean value'.format(value))


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(CURRENT_PATH)
DEBUG = ast.literal_eval(os.environ.get('DEBUG', 'False'))

ADMINS = (
)

MANAGERS = ADMINS

DATABASES = {
 'default' : {
    'ENGINE'    : 'django.db.backends.mysql',
    'NAME'      : os.environ.get('DB_NAME',''),
    "USER"      : os.environ.get('DB_USER',''),
    "PASSWORD"  : os.environ.get('DB_PASS',''),
    "HOST"      : os.environ.get('DB_HOST',''),
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
 )

SECRET_KEY = os.environ.get('SECRET_KEY', '')
if not SECRET_KEY:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    SECRET_KEY = get_random_string(50, chars)

MIDDLEWARE= [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
    'django.contrib.staticfiles',
    'agentex.apps.AgentConfig',
    'storages'
)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'agentex', 'static'),
]

# Static files are on the local filesystem by default
STATIC_URL = '/static/'
STATIC_ROOT = '/static/'

# Media files are on the local filesystem by default
MEDIA_URL = '/images/'
MEDIA_ROOT = '/images/'

# AWS S3 is another supported option for media files
if str2bool(os.getenv('USE_S3', 'False')):
    USE_S3 = True
    # aws settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://s3-{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'core.storage_backends.PublicMediaStorage'

DATA_LOCATION = MEDIA_ROOT + 'data/'
DATA_URL = MEDIA_URL + 'data/'

LOGIN_URL = '/account/login/'

SESSION_COOKIE_NAME='agentexoplanet.sessionid'

EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS       = True
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_HOST_USER     = os.environ.get('EMAIL_USERNAME','')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD','')
EMAIL_PORT          =  587
DEFAULT_FROM_EMAIL  = 'LCO portal <portal@lco.global>'
EMAIL_REPLYTO       = 'agentexoplanet@lco.global'

ALLOWED_HOSTS = ['*']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
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
            'level':'ERROR',
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
if not CURRENT_PATH.startswith('/var/www'):
    try:
        from .local_settings import *
    except ImportError as e:
        if "local_settings" not in str(e):
            raise e
