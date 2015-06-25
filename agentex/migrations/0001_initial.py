# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('awarded', models.DateTimeField(default=datetime.datetime.now, blank=True)),
            ],
            options={
                'db_table': 'dataexplorer_achievement',
                'verbose_name': 'achievement unlocked',
                'verbose_name_plural': 'achievements unlocked',
            },
        ),
        migrations.CreateModel(
            name='AverageSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('values', models.TextField(null=True, blank=True)),
                ('settype', models.CharField(max_length=1, choices=[(b'S', b'Source'), (b'C', b'Calibration'), (b'B', b'Background'), (b'R', b'Reduced'), (b'F', b'Final'), (b'E', b'Error bar')])),
            ],
            options={
                'verbose_name': 'combined lightcurve set',
            },
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'code, no spaces', max_length=20)),
                ('description', models.CharField(help_text=b'brief, publicly readable', max_length=200)),
                ('image', models.FileField(upload_to=b'badge')),
            ],
            options={
                'db_table': 'dataexplorer_badge',
                'verbose_name': 'badge',
            },
        ),
        migrations.CreateModel(
            name='CatSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'object name')),
                ('xpos', models.IntegerField(verbose_name=b'x position on finder image', blank=True)),
                ('ypos', models.IntegerField(verbose_name=b'y position on finder image', blank=True)),
                ('catalogue', models.CharField(max_length=20, verbose_name=b'catalogue name')),
                ('final', models.BooleanField(default=True, verbose_name=b'include in final curve')),
            ],
            options={
                'db_table': 'dataexplorer_catsource',
                'verbose_name': 'catalogue source',
            },
        ),
        migrations.CreateModel(
            name='DataCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display', models.BooleanField(default=False)),
                ('complete', models.BooleanField(default=False)),
                ('calid', models.IntegerField(verbose_name=b'calibrator order')),
                ('person', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dataexplorer_datacollection',
                'verbose_name': 'data collection',
            },
        ),
        migrations.CreateModel(
            name='Datapoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('taken', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('value', models.FloatField(null=True, blank=True)),
                ('pointtype', models.CharField(max_length=1, choices=[(b'S', b'Source'), (b'C', b'Calibration'), (b'B', b'Background'), (b'R', b'Reduced'), (b'F', b'Final'), (b'E', b'Error bar')])),
                ('xpos', models.IntegerField(verbose_name=b'x position', blank=True)),
                ('ypos', models.IntegerField(verbose_name=b'y position', blank=True)),
                ('radius', models.IntegerField(verbose_name=b'aperture radius', blank=True)),
                ('entrymode', models.CharField(default=b'W', max_length=1, choices=[(b'W', b'Web'), (b'M', b'Manual'), (b'N', b'No javascript')])),
                ('offset', models.FloatField(verbose_name=b'distance from source', blank=True)),
                ('coorder', models.ForeignKey(blank=True, to='agentex.DataCollection', help_text=b'point order', null=True)),
            ],
            options={
                'db_table': 'dataexplorer_datapoint',
                'verbose_name': 'data point',
            },
        ),
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fits', models.URLField(blank=True)),
                ('image', models.URLField(null=True, blank=True)),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('telescopeid', models.CharField(max_length=100, blank=True)),
                ('max_x', models.IntegerField(verbose_name=b'max pixels (x)')),
                ('max_y', models.IntegerField(verbose_name=b'max pixels (y)')),
            ],
            options={
                'db_table': 'dataexplorer_datasource',
                'verbose_name': 'data source image',
            },
        ),
        migrations.CreateModel(
            name='Decision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=1, verbose_name=b'decision', choices=[(b'D', b'Dip'), (b'N', b'No Dip'), (b'O', b'Odd'), (b'B', b'Blip'), (b'P', b'Periodic'), (b'S', b'Noise'), (b'R', b'Other')])),
                ('taken', models.DateTimeField(default=datetime.datetime.now)),
                ('current', models.BooleanField(default=False)),
                ('person', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dataexplorer_decision',
                'verbose_name': 'lightcurve decision',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'code, no spaces and no hyphens', max_length=20)),
                ('title', models.CharField(max_length=100)),
                ('start', models.DateTimeField(default=datetime.datetime.now, null=True, blank=True)),
                ('end', models.DateTimeField(default=datetime.datetime.now, null=True, blank=True)),
                ('midpoint', models.DateTimeField(null=True, blank=True)),
                ('numobs', models.IntegerField(default=0, null=True, blank=True)),
                ('finder', models.IntegerField(verbose_name=b'id of finder chart source', blank=True)),
                ('xpos', models.IntegerField(default=0, verbose_name=b'x pos on finder chart')),
                ('ypos', models.IntegerField(default=0, verbose_name=b'y pos on finder chart')),
                ('enabled', models.BooleanField(default=True, help_text=b'show this event on main site')),
                ('illustration', models.FileField(help_text=b'illustration for this event', upload_to=b'illustration', verbose_name=b'illustration', blank=True)),
                ('radius', models.IntegerField(default=10, verbose_name=b'aperture radius')),
            ],
            options={
                'db_table': 'dataexplorer_event',
                'verbose_name': 'transit event',
            },
        ),
        migrations.CreateModel(
            name='Observer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(default=b'LCO', max_length=75)),
                ('organization', models.CharField(max_length=150, blank=True)),
                ('dataexploreview', models.BooleanField(default=True, verbose_name=b'use web interface for dataexplorer')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'observer',
                'verbose_name': 'observer',
            },
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('ra', models.CharField(max_length=100, verbose_name=b'right ascension', blank=True)),
                ('dec', models.CharField(max_length=100, verbose_name=b'declination', blank=True)),
                ('constellation', models.CharField(max_length=100, blank=True)),
                ('magv', models.CharField(max_length=100, verbose_name=b'apparent magnitude V', blank=True)),
                ('inclination', models.FloatField(null=True, verbose_name=b'inclination of planet orbit', blank=True)),
                ('period', models.FloatField(null=True, verbose_name=b'period of planet orbit (days)', blank=True)),
                ('rstar', models.FloatField(null=True, verbose_name=b'radius of host star', blank=True)),
                ('ap', models.FloatField(null=True, verbose_name=b'semi-major axis', blank=True)),
                ('mass', models.FloatField(null=True, verbose_name=b'mass of host star', blank=True)),
                ('description', models.TextField()),
                ('finderchart', models.FileField(help_text=b'Image with a clearly marked up target position', upload_to=b'finderchart', verbose_name=b'Finder chart', blank=True)),
                ('finderchart_tb', models.FileField(help_text=b'Image with a clearly marked up target position', upload_to=b'finderchart/thumb', verbose_name=b'Finder chart thumbnail', blank=True)),
            ],
            options={
                'db_table': 'dataexplorer_target',
                'verbose_name': 'transiting exoplanet target',
            },
        ),
        migrations.AddField(
            model_name='decision',
            name='planet',
            field=models.ForeignKey(to='agentex.Event'),
        ),
        migrations.AddField(
            model_name='decision',
            name='source',
            field=models.ForeignKey(to='agentex.CatSource'),
        ),
        migrations.AddField(
            model_name='datasource',
            name='event',
            field=models.ForeignKey(to='agentex.Event'),
        ),
        migrations.AddField(
            model_name='datasource',
            name='target',
            field=models.ForeignKey(to='agentex.Target'),
        ),
        migrations.AddField(
            model_name='datapoint',
            name='data',
            field=models.ForeignKey(to='agentex.DataSource'),
        ),
        migrations.AddField(
            model_name='datapoint',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='datacollection',
            name='planet',
            field=models.ForeignKey(to='agentex.Event'),
        ),
        migrations.AddField(
            model_name='datacollection',
            name='source',
            field=models.ForeignKey(blank=True, to='agentex.CatSource', null=True),
        ),
        migrations.AddField(
            model_name='catsource',
            name='data',
            field=models.ForeignKey(to='agentex.DataSource'),
        ),
        migrations.AddField(
            model_name='averageset',
            name='planet',
            field=models.ForeignKey(to='agentex.Event'),
        ),
        migrations.AddField(
            model_name='averageset',
            name='star',
            field=models.ForeignKey(blank=True, to='agentex.CatSource', null=True),
        ),
        migrations.AddField(
            model_name='achievement',
            name='badge',
            field=models.ForeignKey(to='agentex.Badge'),
        ),
        migrations.AddField(
            model_name='achievement',
            name='person',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='achievement',
            name='planet',
            field=models.ForeignKey(blank=True, to='agentex.Event', help_text=b'planet', null=True),
        ),
    ]
