# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agentex', '0009_datapoint_coordsource'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datapoint',
            name='coordsource',
        ),
    ]
