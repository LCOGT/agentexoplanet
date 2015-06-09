import os
import pyfits
from datetime import datetime
import atpy
import aplpy
import subprocess

# Preamble so we can use Django's DB API
#os.environ['DJANGO_SETTINGS_MODULE'] = 'timeallocation.settings'

from agentex.models import DataSource, Event, Target, CatSource
from settings import DATA_LOCATION

path = '/Users/eg/Sites/data/'

#url1 = "complete/extra/GJ1214/"
urlj = 'jpgs/' 
urlf = 'fits/'
#urlj =  "http://localhost/data/M51-R/"

def importfits(ev,tg,url):
    fitsdir = "%s%s%s" % (path,url,urlf)
    print "Listing %s" % fitsdir
    ls = os.listdir(fitsdir)
    listf = []
    listj = []
    i = 0

    for l in ls:
        if l.endswith('.fits'):
            listf.append(l)
    
    e = Event.objects.get(id=int(ev))
    target = Target.objects.get(id=int(tg))
    print "%s : %s\n" % (target.name,e.title)
    for lf in listf:
        datapath = "%s%s%s%s" % (path,url,urlf,lf)
        print "reading from %s" % datapath
        head = pyfits.getheader(datapath)
        imagej = lf.replace('.fits','.jpg')
        fitsurl = "/%s%s%s" % (url,urlf,lf)
        try:
            print head['TELESCOP']
        except:
            print "Not FTN or FTS"
        if head['TELESCOP'] == 'Faulkes Telescope North' or head['TELESCOP'] == 'Faulkes Telescope South': 
            # FTN/S data
            timestamp = datetime.strptime(head['DATE-OBS'], "%Y-%m-%dT%H:%M:%S.%f")
            maxx = int(head['CCDXIMSI'])
            maxy = int(head['CCDYIMSI'])
            print maxx,maxy
        else:
            # Sedgwick data
            timestamp = datetime.strptime(head['DATE-OBS'], "%Y-%m-%dT%H:%M:%S")
            maxx= int(head['NAXIS1'])
            maxy = int(head['NAXIS2'])
        ds = DataSource(fits = fitsurl,
                    event=e,
                    target=target,
                    timestamp=timestamp,
                    telescopeid=head['TELESCOP'],
                    max_x=maxx,
                    max_y=maxy,
                    )
        try:
            imageurl = "/%s%s%s" % (url,urlj,imagej)
            ds.image = imageurl
        except:
            print "failed to find JPG for lf"
        ds.save()
        i += 1
        print "Saved %s at %s" % (ds.id,datapath)
    ds = DataSource.objects.filter(event=e).order_by('timestamp')
    e.numobs = ds.count()
    e.start = ds[0].timestamp
    e.end = ds[ds.count()-1].timestamp
    e.midpoint = ds[ds.count()/2].timestamp
    e.save()
    
def correctimages(event):
    ds = DataSource.objects.filter(event=event)
    for d in ds:
        ipath = d.image.split('/')
        fpath = d.fits.split('/')
        d.fits = "/%s/%s/%s" % (fpath[1],fpath[3],fpath[-1])
        d.image = "/%s/%s/%s" % (ipath[1],ipath[3],ipath[-1])
        d.save()
        
def findsources(dataid,datapath):
    d = DataSource.objects.filter(id=dataid)
    dfile = '%s%s' % (datapath,d[0].fits)
    #dfile = '%s%s/astrometry-solution.fits' % (path,url)
    dc = pyfits.open(dfile)
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
    ra_max = max(ra1)
    dec_max = max(dec1)
    ra_min = min(ra1)
    dec_min = min(dec1)
   # print head['CCDXIMSI'],head['CCDXIMSI'],ra_min, ra_max, dec_min,dec_max
    t = atpy.Table(catalog='USNO-A2', ra=ra, dec=dec, radius=2.*r, type='vo_conesearch')
    t4 = t.where((t.RA > ra_min) & (t.RA < ra_max) & (t.DEC > dec_min) & (t.DEC < dec_max) )
    print len(t4)
    f.add_grid()
    f.show_grayscale()
    if t4:
        f.show_markers(t4.RA,t4.DEC,c='r', s= 6, alpha=0.5,edgecolor='none')
    imagej = dfile.replace('.fits','.png')
    print imagej
    f.save(imagej)
    x,y = f.world2pixel(t4.RA,t4.DEC)
    for i,val in enumerate(t4.id):
        #print i, val,int(x[i]),int(y[i]),ra,dec
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
    f.close()

def createjpgs(url1):
    fitsdir = "%s%s%s" % (path,url1,urlf)
    print "Listing %s" % fitsdir
    ls = os.listdir(fitsdir)
    for l in ls:
        filen = '%s%s' % (fitsdir,l)
        filej = filen.replace('.fits','.jpg')
        # try:
        args = ["mJPEG", "-out", filej, "-gray", filen,"0s","98%", "linear"]
        print args
        subprocess.check_call(args)
        #     print 'Saved %s%s' % (fitsdir,filej)
        # except:
        #     print "could not create file %s" % filej

def f(x,y,z):
     if x.endswith('.fits'):
         return y.append(x)
     elif x.endswith('jpg'):
         return z.append(x)

         
