# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agentex', '0002_auto_20150622_1005'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='etd_pl',
            field=models.URLField(null=True, verbose_name=b'Exoplanet Transit Database: Planet', blank=True),
        ),
        migrations.AddField(
            model_name='target',
            name='simbad_pl',
            field=models.URLField(null=True, verbose_name=b'Simbad: Planet', blank=True),
        ),
        migrations.AddField(
            model_name='target',
            name='simbad_st',
            field=models.URLField(null=True, verbose_name=b'Simbad: Star', blank=True),
        ),
    ]
