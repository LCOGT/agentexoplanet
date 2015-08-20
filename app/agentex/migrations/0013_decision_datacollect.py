# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agentex', '0012_remove_decision_datacollect'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='datacollect',
            field=models.BooleanField(default=False),
        ),
    ]
