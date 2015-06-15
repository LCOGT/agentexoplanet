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
from django.db import models

class Event(models.Model):
    hostid = models.CharField(max_length=75)
    name = models.CharField(max_length=75)
    current = models.BooleanField(default=False)
    slotlist = models.CharField(max_length=75)
    start = models.DateTimeField()
    end = models.DateTimeField()
    site = models.CharField(max_length=75,blank=True,null=True)
    class Meta:
        verbose_name = u'show me stars event'
    def __unicode__(self):
        return "%s %s %s" % (self.name,self.start.isoformat(),self.site)
        