from django.core.management.base import BaseCommand, CommandError
from agentex.models import DataSource, Event, Decision, CatSource

class Command(BaseCommand):
    args = '<event_id>'
    help = 'Create CatSource objects for a given Planet'

    def handle(self, *args, **options):
        try:
            planet = Event.objects.get(name=args[0])
            decs = Decision.objects.filter(planet=planet)
            for dec in decs:
                c = dec.source
                cats = CatSource.objects.filter(xpos__lt=c.xpos+5,ypos__lt=c.ypos+5,xpos__gt=c.xpos-5,ypos__gt=c.ypos-5,data__event=planet)
                if cats:
                    dec.source = cats[0]
                    dec.save()
                    print dec.person.username, dec.current, c.name
        except Exception, e:
            print e