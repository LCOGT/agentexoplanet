# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agentex', '0005_delete_lastlogins'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapoint',
            name='ident',
            field=models.CharField(default='identifier', max_length=20),
            preserve_default=False,
        ),
    ]
