#!/usr/bin/env python

import os
import sys
sys.stdout = sys.stderr

# Add the parent app folder to the pythonpath
sys.path.append('/var/www')
sys.path.append('/var/www/agentexoplanet')
os.environ['DJANGO_SETTINGS_MODULE'] = 'agentexoplanet.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
