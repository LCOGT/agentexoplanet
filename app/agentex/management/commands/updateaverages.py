from django.core.management.base import BaseCommand, CommandError
from agentex.models import AverageSet, Datapoint, Event
from datetime import datetime, timedelta
from agentex.views import averagecals_async, supercaldata

class Command(BaseCommand):
    args = '<event_name> <force>'
    help = 'Update the AverageSets but only if that planet has had new measurements recently'

    def add_arguments(self, parser):
        parser.add_argument('--event_id', type=str)
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        now = datetime.now()
        if options.get('event_id', None):
            planets = Event.objects.filter(slug=options['event_id'])
        else:
            planets = Event.objects.filter(enabled=True)
        for planet in planets:
            latest = Datapoint.objects.filter(data__event=planet).latest('taken')
            latest_aveset = AverageSet.objects.filter(planet=planet).latest('updated')
            if (latest.taken > latest_aveset.updated ) or options.get('force',False):
                self.stdout.write("Updating {}".format(planet.title))
                averagecals_async(planet)
                ### Create final dataset and store as an average set
                result = supercaldata(None,planet.slug)
                final = [{'type' : 'F', 'data':result[1]},{'type' : 'E', 'data':result[3]}]
                for s in final:
                    ave_set, created = AverageSet.objects.get_or_create(star=None,planet=planet,settype=s['type'])
                    ave_set.values = ";".join([str(i) for i in s['data']])
                    ave_set.updated = now
                    ave_set.save()
            else:
                self.stdout.write("No update needed for %s\n" % planet.title)
