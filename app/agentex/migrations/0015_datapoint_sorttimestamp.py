# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agentex', '0014_remove_decision_datacollect'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapoint',
            name='sorttimestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
