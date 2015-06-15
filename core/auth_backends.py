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

            
