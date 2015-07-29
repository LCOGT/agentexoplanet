#!/usr/bin/env python
import sys, os, re, urllib2, datetime, random
from datetime import datetime, timedelta, date
from odin.dataexplorer.models import ObservationStats

import MySQLdb

# Start connection
db = MySQLdb.connect(user="edward", passwd="93Hp8HVm", db="faulkes", host="db01sba")

sql_objects = "SELECT obs_id,when_taken,weight,last_viewed,img_url,views from rti_stats_observations"
obj = db.cursor()
obj.execute(sql_objects)


for o in obj:
    obs = ObservationStats(imagearchive=o[0],
                            whentaken=o[1],
                            weight=o[2],
                            last_viewed= o[3],
                            img_url= o[4],
                            views= o[5])
    obs.save()
    print "Saved %s %s" % (obs.imagearchive,obs.views)
    
