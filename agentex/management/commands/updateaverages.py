from django.core.management.base import BaseCommand, CommandError
from agentex.models import AverageSet, Datapoint, Event
from datetime import datetime, timedelta
from agentex.views import averagecals_async, supercaldata

class Command(BaseCommand):
    args = '<event_name> <force>'
    help = 'Update the AverageSets but only if that planet has had new measurements recently'

    def handle(self, *args, **options):
        force = False
        if args:
            planets = Event.objects.filter(name=args[0])
            try:
                if args[1] == 'force':
                    force = True
            except:
                pass
        else:
            planets = Event.objects.filter(enabled=True)
        for planet in planets:
            latest = Datapoint.objects.filter(data__event=planet).latest('taken')
            if (datetime.now() - latest.taken < timedelta(minutes=10)) or force:
                averagecals_async(planet)
                ### Create final dataset and store as an average set
                result = supercaldata(None,planet)
                final = [{'type' : 'F', 'data':result[1]},{'type' : 'E', 'data':result[3]}]
                for s in final:
                    a = AverageSet.objects.get_or_create(star=None,planet=planet,settype=s['type'])
                    a[0].values = ";".join([str(i) for i in s['data']])
                    a[0].save()
            else:
                self.stdout.write("No update needed for %s\n" % planet.title)
            