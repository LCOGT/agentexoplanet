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
        dp_list = Datapoint.objects.all()
        total = dp_list.count()
        update_datapoints(dp_list, total)


def update_datapoints(dp_list, total): 
    for counter, d in enumerate(dp_list):
        d.ident = d.data.event.name
        d.tstamp = mktime(d.data.timestamp.timetuple())
        d.save()
        progress = float(counter)/float(total)
        bar = '#'*int(progress*20.)
        sys.stdout.write('\r[{0}] {1}% - {2}'.format(bar, progress*100., counter))
        sys.stdout.flush()