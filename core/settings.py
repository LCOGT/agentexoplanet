# Django settings for observing project.

import os
import platform
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
from django.utils.crypto import get_random_string


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
LOCAL_DEVELOPMENT = False if CURRENT_PATH.startswith('/var/www') else True

DEBUG = False if LOCAL_DEVELOPMENT == False else True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Edward Gomez', 'egomez@lcogt.net'),
)

MANAGERS = ADMINS

# TEST authentication details

ADMIN_LOGIN = 'admin'
ADMIN_PASSWORD = 'sha1$4e987$afbcf42e21bd417fb71db8c66b321e9fc33051de'

# END of TEST

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

if not LOCAL_DEVELOPMENT:
    MEDIA_DIR = '/agentexoplanet/media/'
else:
    MEDIA_DIR = '/media/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = CURRENT_PATH + MEDIA_DIR

    
STATIC_DIR = '/static/'
STATIC_ROOT = CURRENT_PATH + '/static/'
STATIC_URL = STATIC_DIR

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
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

TEMPLATE_CONTEXT_PROCESSORS = (
   'django.core.context_processors.media',
   'django.contrib.auth.context_processors.auth',
   'django.contrib.messages.context_processors.messages',
   'django.core.context_processors.static'
)

if not LOCAL_DEVELOPMENT:
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )
else:
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )  

CACHE_MIDDLEWARE_SECONDS = '1'

AUTHENTICATION_BACKENDS = (
    'auth_backends.LCOAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

ROOT_URLCONF = 'urls'

if not LOCAL_DEVELOPMENT:
    LOGIN_REDIRECT_URL = 'http://lcogt.net/agentexoplanet/'

    LOGIN_URL = 'http://lcogt.net/agentexoplanet/account/login/'

    TEMPLATE_DIRS = (
        CURRENT_PATH + '/templates',
        """
        CURRENT_PATH + '/templates/citsci',
        """
    )
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.admin',
        'django.contrib.messages',
        'django.contrib.comments',
        'agentex',
        'showmestars',
    )
else:
    INTERNAL_IPS = ('127.0.0.1',)

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )
    
    LOGIN_URL = 'http://localhost:8000/account/login/'

    LOGIN_REDIRECT_URL = '/'

    TEMPLATE_DIRS = (
        CURRENT_PATH + "/templates"
    )  
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.comments',
        'django.contrib.admin',
        'agentex',
        'showmestars',
        'debug_toolbar',
        #'djcelery'
    )

#djcelery.setup_loader()
# Our celery broker backend stuff (where RabbitMQ is installed)
BROKER_HOST = "172.16.5.120"
BROKER_PORT = 5672
"""
    RabbitMQ must be installed and configured on BROKER_HOST.
    See http://mathematism.com/2010/02/16/message-queues-django-and-celery-quick-start/
    
    After a default RabbitMQ install, run:
        rabbitmqctl add_user telops telops
        rabbitmqctl add_vhost telops
        rabbitmqctl set_permissions -p telops telops ".*" ".*" ".*"
        
"""
BROKER_VHOST = "citsci"
BROKER_USER = "citsci"
BROKER_PASSWORD = "citsci"

BASE_URL = "/agentexoplanet/"

if not LOCAL_DEVELOPMENT:
    DATA_LOCATION = CURRENT_PATH + '/media/data'
    DATA_URL = '/agentexoplanet/media/data'
else:
    DATA_LOCATION ='/Volumes/Tardis-type40/AgentExoplanetData/agentexdata'
    DATA_URL = 'http://localhost/agentexdata'
