from django.core.management.base import BaseCommand, CommandError
from agentex.models import Datapoint, Event
from datetime import datetime, timedelta
from time import mktime
import sys

class Command(BaseCommand):
    args = '<event_name>'
    help = 'Update existing Datapoints with planetcode and datasource timestamp'

    def handle(self, *args, **options):
        sys.stdout.write('Initialising queryset')
        codes = {}
        for e in Event.objects.all():
            codes[e.name] = e.id
        # Update datapoint to use planet ID
        dps = Datapoint.objects.all()
        for k,v in codes.items():
            dps.filter(ident=k).update(planetid=v)
