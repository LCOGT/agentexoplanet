from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model
from django.conf import settings
from django.contrib.auth.models import User, check_password
from django.contrib.auth.backends import ModelBackend
import MySQLdb
import hashlib
from odin.settings import DATABASES as dbc
from odin.obsapp.models import Observer

def matchDrupalPass(username,password):
    # Retreive the database user information from the settings
    db = MySQLdb.connect(user=dbc['website']['USER'], passwd=dbc['website']['PASSWORD'], db=dbc['website']['NAME'], host=dbc['website']['HOST'])

    # Match supplied user name to one in Drupal database
    sql_users = "SELECT name, pass, mail FROM users WHERE name='%s'" % username
    drupal = db.cursor()
    drupal.execute(sql_users)
    user = drupal.fetchone()
    drupal.close()
    db.close()
    if user:
        if (hashlib.md5(password).hexdigest() == user[1]):
            return user[2], None, None
    else:
        return False
        
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
        fns =  (matchDrupalPass(username, password), matchRTIPass(username, password))
        for response in fns:
            if (response):
                return checkUserObject(response,username,password)
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None  

            
