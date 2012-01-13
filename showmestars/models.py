from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Event(models.Model):
    hostid = models.CharField(max_length=75)
    name = models.CharField(max_length=75)
    current = models.BooleanField(default=False)
    slotlist = models.CharField(max_length=75)
    start = models.DateTimeField()
    end = models.DateTimeField()
    site = models.CharField(max_length=75,blank=True,null=True)
    def __unicode__(self):
        return "%s %s %s" % (self.name,self.start.isoformat(),self.site)
        