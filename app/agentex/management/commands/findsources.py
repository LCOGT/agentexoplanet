from django.core.management.base import BaseCommand, CommandError
from agentex.models import DataSource, Event, Target, CatSource
import os #, pyfits
from astropy.io import fits
from astropy import wcs
from astropy.table import Table
import astropy.coordinates as coord
import astropy.units as u
from datetime import datetime
import aplpy
import numpy as np
from core.settings import DATA_LOCATION
from astroquery.vizier import Vizier

class Command(BaseCommand):
    args = '<event_id>'
    help = 'Create CatSource objects for a given Planet'

    def handle(self, *args, **options):
        args = [u'wasp12b']
        try:
            planet = Event.objects.get(name=args[0])
            d = DataSource.objects.filter(id=planet.finder)
            print d
            dfile = '%s%s' % (DATA_LOCATION,d[0].fits)
            #dc = pyfits.open(dfile)
            dc = fits.open(dfile)
            #### Map WCS coords to pixel values for the first file in the dataset
            f = aplpy.FITSFigure(dc[0])
            head = dc[0].header
            print head['TELESCOP']
            ra= head['CRVAL1'] #291.75
            dec = head['CRVAL2'] #1.38
            if (head['TELESCOP'] == 'SQA-0m8' or head['TELESCOP'] == 'SBA-0m8'):
                xpix  = [0,1024,0,1024]
                ypix = [0,0,1024,1024]
                r = 0.2
            if (head['TELESCOP'] == 'Faulkes Telescope North' or head['TELESCOP'] == 'Faulkes Telescope South'):
                r = head['PIXSCALE']*head['CCDXIMSI']/3600. #0.0792178
                # Change to 0,0 1024,1024 if in Northern Hem
                xpix  = [0,head['CCDXIMSI'],0,head['CCDXIMSI']]
                ypix = [0,0,head['CCDXIMSI'],head['CCDXIMSI']]
            ra1, dec1 = f.pixel2world(xpix,ypix)
            #ra1, dec1 = w.wcs_pix2world(xpix, ypix, 1) # argument 1 starts from (1,1)
            ra_max = max(ra1)
            dec_max = max(dec1)
            ra_min = min(ra1)
            dec_min = min(dec1)
            print 'dec_min=', dec_min
            #print head['CCDXIMSI'],head['CCDXIMSI'],ra_min, ra_max, dec_min,dec_max
            #t = atpy.Table(catalog='USNO-A2', ra=ra, dec=dec, radius=2.*r, type='vo_conesearch')
            t = Vizier.query_region(coord.SkyCoord(ra=ra, dec=dec,
                                            unit = (u.deg, u.deg),
                                            frame='icrs'),
                                            radius=(2.*r)*u.deg,
                                            catalog='USNO-A2.0'
                                            )
            t_table = t['I/252/out']
            print 't_table is', t_table
            print 'colnames:', t_table.colnames
            #print "t['RA'] > ra_min is", (t['RA'] > ra_min)
            #t4 = np.where((t_table['RAJ2000'] > ra_min) & (t_table['RAJ2000'] < ra_max) & (t_table['DEJ2000'] > dec_min) & (t_table['DEJ2000'] < dec_max))
            #t4 = np.where((t['RA'] > ra_min) & (t['RA'] < ra_max) & (t['DEC'] > dec_min) & (t['DEC'] < dec_max))

            t4 = Table([[],[]],names=['RA','DEC'])
            for i in range(0,len(t_table)):
                print i
                if (t_table['RAJ2000'][i] > ra_min) & (t_table['RAJ2000'][i] < ra_max):
                    if (t_table['DECJ2000'][i] > dec_min) & (t_table['DECJ2000'][i] < dec_max):
                        t4.add_row([t_table['RAJ2000'][i],t_table['DECJ2000'][i]])

            print 't4 is', t4
            print len(t4)
            x,y = f.world2pixel(t4['RA'],t4['DEC'])
            #x,y = w.wcs_world2pix(t4.RA,t4.DEC)
            for i,val in enumerate(t4.id):
                if (x[i] >0 and y[i] >0):
                    cat = CatSource(name=val,
                                 xpos=int(x[i]),
                                 ypos=int(y[i]),
                                 catalogue='USNO-A2.0',
                                 data=d[0])
                    try:
                        cat.save()
                        print "Saved %s" % val
                    except:
                        print "error on save %s" % val
        except Exception,e:
            print "Could not find planet %s - %s" % (args[0],e)
