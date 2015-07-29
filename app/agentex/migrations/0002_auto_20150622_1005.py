# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agentex', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='exoplanet_enc_pl',
            field=models.URLField(null=True, verbose_name=b'Exoplanet Encyclopaedia: Planet', blank=True),
        ),
        migrations.AddField(
            model_name='target',
            name='exoplanet_enc_st',
            field=models.URLField(null=True, verbose_name=b'Exoplanet Encyclopaedia: Star', blank=True),
        ),
    ]
