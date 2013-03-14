from django.core.management.base import BaseCommand, CommandError
from agentex.models import AverageSet, Datapoint, Event
from datetime import datetime, timedelta
from agentex.views import averagecals_async

class Command(BaseCommand):
    args = '<event_name>'
    help = 'Update the AverageSets but only if that planet has had new measurements recently'

    def handle(self, *args, **options):
        if args:
            planets = Event.objects.filter(name=args[0])
        else:
            planets = Event.objects.filter(enabled=True)
        for planet in planets:
            latest = Datapoint.objects.filter(data__event=planet).latest('taken')
            if datetime.now() - latest.taken > timedelta(minutes=10):
                averagecals_async(planet)
            else:
                self.stdout.write("No update needed for %s" % planet.title)
            