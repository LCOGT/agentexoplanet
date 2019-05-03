from astropy.io import fits
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from numpy import floor
import os

from agentex.models import DataSource, Event,CatSource

class Command(BaseCommand):
    args = '<event_id>'
    help = 'Create DataSource objects for FITS files. This is only to be run locally'

    def add_arguments(self, parser):
        parser.add_argument('--event_id', type=str)

    def handle(self, *args, **options):
        e = Event.objects.get(slug=options['event_id'])
        urlj = 'jpgs'
        urlf = 'fits'
        fitsdir = "%s/%s/%s/" % (settings.DATA_LOCATION,e.slug,urlf)
        self.stdout.write("Looking in {}".format(fitsdir))
        ls = os.listdir(fitsdir)
        listf = []
        listj = []
        i = 0
        for l in ls:
            if l.endswith('.fits.fz'):
                listf.append(l)

        self.stdout.write('{} files for {}'.format(len(listf), e.title))
        for lf in listf:
            datapath = "%s/%s/%s/%s" % (settings.DATA_LOCATION,e.slug,urlf,lf)
            self.stdout.write('reading from %s' % datapath)
            #head = pyfits.getheader(datapath)
            hdu = fits.open(datapath)
            head = hdu[1].header
            imagej = lf.replace('.fits.fz','.jpg')
            fitsurl = "/%s/%s/%s" % (e.slug,urlf,lf)
            try:
                self.stdout.write('Telescope %s\n' % head['TELESCOP'])
            except:
                self.stdout.write('Not FTN or FTS\n')
            # LCO data
            timestamp = datetime.strptime(head['DATE-OBS'], "%Y-%m-%dT%H:%M:%S.%f")
            maxx= int(head['NAXIS1'])
            maxy = int(head['NAXIS2'])
            telescope_name = "{} at {}".format(head['TELID'], head['SITEID'])
            ds, created = DataSource.objects.get_or_create(fits = fitsurl, event=e)
            ds.timestamp=timestamp
            ds.telescopeid=telescope_name
            ds.max_x=maxx
            ds.max_y=maxy
            try:
                imageurl = "/%s/%s/%s" % (e.slug,urlj,imagej)
                ds.image = imageurl
            except:
                raise CommandError('failed to find JPG for lf')
            ds.save()
            i += 1
            self.stdout.write('Saved %s at %s\n' % (ds.id,datapath))
        ds = DataSource.objects.filter(event=e).order_by('timestamp')
        midpoint = int(floor(ds.count()/2))
        e.numobs = ds.count()
        e.start = ds[0].timestamp
        e.end = ds[ds.count()-1].timestamp
        e.midpoint = ds[midpoint].timestamp
        e.save()

        self.stdout.write('Successfully imported all data for "%s"\n' % e.title)

def f(x,y,z):
     if x.endswith('.fits.fz '):
         return y.append(x)
     elif x.endswith('jpg'):
         return z.append(x)
