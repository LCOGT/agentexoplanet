from django.core.management.base import BaseCommand, CommandError
from agentex.models import DataSource
import os

from django.conf import settings

class Command(BaseCommand):
    help = 'Separate images to be served by Whitenoise and FITS data'

    def handle(self, *args, **options):
        self.stdout.write('Find all DataSources')
        base_path = '/planets/'
        for d in DataSource.objects.all():
            path = os.path.split(d.image)
            new_path = os.path.join(base_path, d.event.slug, path[1])
            # Check full path actually exists
            if os.path.isfile(os.path.join(settings.STATIC_ROOT, new_path)):
                print(new_path)
            else:
                self.stderr.write('File not found: {}'.format(new_path))
