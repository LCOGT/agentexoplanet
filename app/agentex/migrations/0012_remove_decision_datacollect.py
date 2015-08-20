# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agentex', '0011_decision_datacollect'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='decision',
            name='datacollect',
        ),
    ]
