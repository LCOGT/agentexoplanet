from django.core.management.base import BaseCommand, CommandError
from agentex.models import Event, Target

class Command(BaseCommand):
    help = 'Combine  Event and target'

    def handle(self, *args, **options):
        for target in Target.objects.all():
            try:
                event = Event.objects.get(title__contains=target.name)
            except Event.DoesNotExist:
                self.stderr.write("Could not find event matching {}".format(target.name))
                continue

            event.slug = target.name
            event.ra = target.ra
            event.dec = target.dec
            event.constellation = target.constellation
            event.magv = target.magv
            event.inclination = target.inclination
            event.period = target.period
            event.rstar = target.rstar
            event.ap = target.ap
            event.mass = target.mass
            event.description = target.description
            event.finderchart = target.finderchart
            event.finderchart_tb = target.finderchart_tb
            event.exoplanet_enc_st = target.exoplanet_enc_st
            event.exoplanet_enc_pl = target.exoplanet_enc_pl
            event.etd_pl = target.etd_pl
            event.simbad_pl = target.simbad_pl
            event.simbad_st = target.simbad_st

            event.save()
            self.stdout.write("Updated {}".format(event.title))

            target.delete()
            self.stdout.write("Deleting target {}".format(target.name))
