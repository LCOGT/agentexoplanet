from django.core.management.base import BaseCommand, CommandError
from agentex.models import Datapoint
from datetime import datetime, timedelta
from time import mktime
import sys

class Command(BaseCommand):
    args = '<event_name> <force>'
    help = 'Update existing Datapoints with planetcode and datasource timestamp'

    def handle(self, *args, **options):
        sys.stdout.write('Initialising queryset')
        dps = Datapoint.objects.all()
        total = dps.count()
        for counter, d in enumerate(dps):
            d.ident = d.data.event.name
            d.tstamp = mktime(d.data.timestamp.timetuple())
            d.save()
            progress = float(counter)/float(total)
            bar = '#'*(int(progress)*20)
            sys.stdout.write('\r[{0}] {1}% - {2}'.format(bar, progress, counter))
            sys.stdout.flush()