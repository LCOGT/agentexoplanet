# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agentex', '0016_remove_datapoint_sorttimestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapoint',
            name='tstamp',
            field=models.IntegerField(default=1, verbose_name=b'unix timestamp', blank=True),
            preserve_default=False,
        ),
    ]
