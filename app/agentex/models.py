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
from datetime import datetime
from django.contrib.auth.models import User
from calendar import timegm
from json import dumps,loads
TYPECHOICE = (
('S','Source'),
('C','Calibration'),
('B','Background'),
('R','Reduced'),
('F','Final'),
('E','Error bar')
)
ENTRYCHOICE = (
('W','Web'),
('M','Manual'),
('N','No javascript'),
)

DECISIONS = (
('D','Dip'),
('N','No Dip'),
('O','Odd'),
('B','Blip'),
('P','Periodic'),
('S','Noise'),
('R','Other'),
)
decisions = {
    'dip':'D',
    'nodip':'N',
    'odd':'O',
    'blip':'B',
    'periodic':'P',
    'other':'R',
}

class Target(models.Model):
    name = models.CharField(blank=True, max_length=100) # Wordy name. should be the name of the host star
    ra = models.CharField('right ascension',blank=True, max_length=100)
    dec = models.CharField('declination',blank=True, max_length=100)
    constellation = models.CharField(blank=True, max_length=100)
    magv = models.CharField('apparent magnitude V',blank=True, max_length=100)
    inclination = models.FloatField('inclination of planet orbit',blank=True,null=True)
    period = models.FloatField('period of planet orbit (days)',blank=True,null=True)
    rstar = models.FloatField('radius of host star',blank=True,null=True)
    ap = models.FloatField('semi-major axis',blank=True,null=True)
    mass = models.FloatField('mass of host star',blank=True,null=True)
    description = models.TextField()
    finderchart =  models.FileField('Finder chart',upload_to="finderchart", help_text='Image with a clearly marked up target position',blank=True)
    finderchart_tb =  models.FileField('Finder chart thumbnail',upload_to="finderchart/thumb", help_text='Image with a clearly marked up target position',blank=True)
    exoplanet_enc_pl = models.URLField('Exoplanet Encyclopaedia: Planet', blank=True, null=True)
    exoplanet_enc_st = models.URLField('Exoplanet Encyclopaedia: Star', blank=True, null=True)
    etd_pl = models.URLField('Exoplanet Transit Database: Planet', blank=True, null=True)
    simbad_pl = models.URLField('Simbad: Planet', blank=True, null=True)
    simbad_st = models.URLField('Simbad: Star', blank=True, null=True)
    class Meta:
        verbose_name = u'transiting exoplanet target'
        db_table = u'dataexplorer_target'
    def __unicode__(self):
        return self.name
    
class Event(models.Model):
    name = models.CharField(blank=False, max_length=20, help_text='code, no spaces and no hyphens') # code to be used in URLs i.e. NO spaces
    title = models.CharField(blank=False, max_length=100) # Longer title which can be more wordy
    start = models.DateTimeField(null=True, blank=True, default=datetime.now)
    end = models.DateTimeField(null=True, blank=True, default=datetime.now)
    midpoint = models.DateTimeField(null=True, blank=True)
    numobs = models.IntegerField(blank=True, null=True,default=0)
    finder = models.IntegerField('id of finder chart source',blank=True)
    xpos = models.IntegerField('x pos on finder chart',blank=False,default=0)
    ypos = models.IntegerField('y pos on finder chart',blank=False,default=0)
    enabled = models.BooleanField(default=True,help_text='show this event on main site')
    illustration = models.FileField('illustration',upload_to="illustration", help_text='illustration for this event',blank=True)
    radius = models.IntegerField('aperture radius', blank=False, default=10)
    class Meta:
        verbose_name = u'transit event'
        db_table = u'dataexplorer_event'
    def __unicode__(self):
        return self.name
        
class DataSource(models.Model):
    fits = models.URLField(blank=True)
    image = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    telescopeid = models.CharField(blank=True, max_length=100)
    event = models.ForeignKey(Event)
    target = models.ForeignKey(Target)
    max_x = models.IntegerField('max pixels (x)',blank=False)
    max_y = models.IntegerField('max pixels (y)',blank=False)
    class Meta:
        verbose_name = u'data source image'
        db_table = u'dataexplorer_datasource'
    def __unicode__(self):
        return self.timestamp.isoformat()
    def unixstamp(self):
        return timegm(self.timestamp.timetuple())+1e-6*self.timestamp.microsecond
    def isostamp(self):
        return self.timestamp.isoformat()
    
class CatSource(models.Model):
    name = models.CharField('object name',blank=False,max_length=50)
    data = models.ForeignKey(DataSource)
    xpos = models.IntegerField('x position on finder image', blank=True)
    ypos = models.IntegerField('y position on finder image', blank=True)
    catalogue = models.CharField('catalogue name',blank=False,max_length=20)
    final = models.BooleanField('include in final curve',default=True)
    class Meta:
        verbose_name = "catalogue source"
        db_table = u'dataexplorer_catsource'
    def __unicode__(self):
        return self.name
    
class DataCollection(models.Model):
    person = models.ForeignKey(User)
    planet = models.ForeignKey(Event)
    display = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    calid = models.IntegerField('calibrator order',blank=False,null=False)
    source = models.ForeignKey(CatSource,blank=True, null=True)
    class Meta:
        verbose_name = u'data collection'
        db_table = u'dataexplorer_datacollection'
    def __unicode__(self):
        val = "%s" % self.planet.title
        return val
    
class Datapoint(models.Model):
    data = models.ForeignKey(DataSource)
    taken = models.DateTimeField(blank=True, default=datetime.now)
    value = models.FloatField(blank=True,null=True)  
    user = models.ForeignKey(User)
    pointtype = models.CharField(blank=False,max_length=1,choices=TYPECHOICE)
    coorder = models.ForeignKey(DataCollection,blank=True, null=True, help_text='point order')
    xpos = models.IntegerField('x position', blank=True)
    ypos = models.IntegerField('y position', blank=True)
    radius = models.IntegerField('aperture radius', blank=True)
    entrymode = models.CharField(blank=False,max_length=1,choices=ENTRYCHOICE,default='W')
    offset = models.FloatField('distance from source',blank=True)
    class Meta:
        verbose_name = u'data point'
        db_table = u'dataexplorer_datapoint'
    class Admin:
        list_display = ('event',)
        search_fields = ('user',)
    def __unicode__(self):
        return self.taken.isoformat()
            
class Decision(models.Model):
    source = models.ForeignKey(CatSource)
    value = models.CharField('decision',blank=False,max_length=1,choices=DECISIONS)
    person = models.ForeignKey(User)
    planet = models.ForeignKey(Event)
    taken = models.DateTimeField(default=datetime.now,blank=False)
    current = models.BooleanField(default=False)
    class Meta:
        verbose_name = u'lightcurve decision'
        db_table = u'dataexplorer_decision'
    def __unicode__(self):
        return self.source.name
        
class AverageSet(models.Model):
    planet = models.ForeignKey(Event)
    star = models.ForeignKey(CatSource,blank=True,null=True)
    values = models.TextField(null=True,blank=True)
    settype = models.CharField(blank=False,max_length=1,choices=TYPECHOICE)
    class Meta:
        verbose_name = u'combined lightcurve set'
    @property 
    def data(self):
        return [float(x) for x in self.values.split(';')]
    def __unicode__(self):
        return u"%s" % (self.planet.title)
        
class Badge(models.Model):
    name = models.CharField(blank=False, max_length=20, help_text='code, no spaces')
    description = models.CharField(blank=False, max_length=200, help_text='brief, publicly readable')
    image = models.FileField(upload_to="badge",blank=False)
    class Meta:
        verbose_name = u'badge'
        db_table = u'dataexplorer_badge'
    def __unicode__(self):
        return self.name

class Achievement(models.Model):
    person = models.ForeignKey(User)
    awarded = models.DateTimeField(blank=True, default=datetime.now)
    badge = models.ForeignKey(Badge)
    planet = models.ForeignKey(Event,blank=True, null=True,help_text='planet')
    class Meta:
        verbose_name = u'achievement unlocked'
        verbose_name_plural = u'achievements unlocked'
        db_table = u'dataexplorer_achievement'
    def __unicode__(self):
        if self.planet:
            t = "%s - %s - %s" % (self.badge.name,self.person.username,self.planet.title)
        else:
            t = "%s - %s" % (self.badge.name,self.person.username)
        return t
        
class Observer(models.Model):
    user = models.OneToOneField(User, unique=True,)
    tag = models.CharField(max_length=75, blank=False,default="LCO")
    organization = models.CharField(max_length=150, blank=True)
    dataexploreview = models.BooleanField("use web interface for dataexplorer", default=True)
    class Meta:
        db_table = u'observer'
        verbose_name = "observer"
    def __unicode__(self):
        return self.user.username
    