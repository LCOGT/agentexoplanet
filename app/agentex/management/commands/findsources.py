from django.core.management.base import BaseCommand, CommandError
from agentex.models import DataSource, Event, CatSource
import os #, pyfits
from astropy.io import fits
from astropy import wcs
from astropy.table import Table
import astropy.coordinates as coord
import astropy.units as u
from datetime import datetime
import numpy as np

from django.conf import settings

from astroquery.vizier import Vizier

class Command(BaseCommand):
    args = '<event_id>'
    help = 'Create CatSource objects for a given Planet. For local use only.'

    def add_arguments(self, parser):
        parser.add_argument('--event_id', type=str)

    def handle(self, *args, **options):

        try:
            planet = Event.objects.get(slug=options['event_id'])
            d = DataSource.objects.get(id=planet.finder)
            hdu = fits.open(settings.DATA_LOCATION+d.fits[1:])
            w = wcs.WCS(hdu[1].header)
            ra = hdu[1].header['ra']
            dec = hdu[1].header['dec']
            r = hdu[1].header['NAXIS1']*hdu[1].header['PIXSCALE']/3600.
            sc_coord = coord.SkyCoord(ra=ra, dec=dec,
                        unit=(u.hourangle, u.deg),
                        frame='icrs')

            v = Vizier(column_filters={"R1mag":"<18"}, row_limit=4000)
            t = v.query_region(sc_coord,
                                    radius=2*u.deg,
                                    catalog='USNO-B1.0'
                                    )
            t_table = t['I/284/out']
            coords_pix = [[0, hdu[1].header['NAXIS2']],[hdu[1].header['NAXIS1'], hdu[1].header['NAXIS2']],
                            [0, 0],[hdu[1].header['NAXIS1'], 0]]

            coords = w.wcs_pix2world(coords_pix,1)
            t1 = t_table[t_table['RAJ2000'] > coords[2][0]]
            t2 = t1[t1['RAJ2000'] < coords[1][0]]
            t3 = t2[t2['DEJ2000'] > coords[3][1]]
            t4 = t3[t3['DEJ2000'] < coords[0][1]]
            for row in t4:
                val = row['USNO-B1.0']
                x,y = w.wcs_world2pix(row['RAJ2000'],row['DEJ2000'],1 )
                print(x,y)
                cat = CatSource(name=val,
                             xpos=int(x),
                             ypos=int(y),
                             catalogue='USNO-B1.0',
                             data=d)
                try:
                    cat.save()
                    self.stdout.write("Saved %s" % val)
                except:
                    self.stdout.write("error on save %s" % val)
        except Exception as e:
            self.stdout.write("Could not find planet %s - %s" % (options['event_id'],e))
