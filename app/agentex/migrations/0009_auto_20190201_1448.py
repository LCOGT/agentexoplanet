# Generated by Django 2.1.3 on 2019-02-01 14:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agentex', '0008_auto_20181130_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='averageset',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='event',
            name='finderchart',
            field=models.CharField(blank=True, choices=[('finderchart/OGLETR132b-finder.jpg', 'OGLETR132b-finder.jpg'), ('finderchart/corot2b.jpg', 'corot2b.jpg'), ('finderchart/QATAR1b-finder.jpg', 'QATAR1b-finder.jpg'), ('finderchart/Hat-P-25b-finder.jpg', 'Hat-P-25b-finder.jpg'), ('finderchart/Wasp2b-finder.jpg', 'Wasp2b-finder.jpg'), ('finderchart/TrES3b-finder.jpg', 'TrES3b-finder.jpg'), ('finderchart/Hat-P-8b-finder.jpg', 'Hat-P-8b-finder.jpg'), ('finderchart/Wasp43b-finder.jpg', 'Wasp43b-finder.jpg')], help_text='Image with a clearly marked up target position', max_length=100, verbose_name='Finder chart'),
        ),
        migrations.AlterField(
            model_name='event',
            name='finderchart_tb',
            field=models.CharField(blank=True, choices=[('finderchart/thumb/TrES3b-finder-thumb2.jpg', 'TrES3b-finder-thumb2.jpg'), ('finderchart/thumb/Hat-P-25b-finder-thumb2.jpg', 'Hat-P-25b-finder-thumb2.jpg'), ('finderchart/thumb/corot2b-finder.thumb.jpg', 'corot2b-finder.thumb.jpg'), ('finderchart/thumb/Hat-P-8b-finder-thumb2.jpg', 'Hat-P-8b-finder-thumb2.jpg'), ('finderchart/thumb/Wasp2b-finder-thumb2.jpg', 'Wasp2b-finder-thumb2.jpg'), ('finderchart/thumb/OGLETR132b-finder-thumb2.jpg', 'OGLETR132b-finder-thumb2.jpg'), ('finderchart/thumb/corot2b-finder.thumb.lg.jpg', 'corot2b-finder.thumb.lg.jpg'), ('finderchart/thumb/QATAR1b-finder-thumb2.jpg', 'QATAR1b-finder-thumb2.jpg'), ('finderchart/thumb/Wasp43b-finder-thumb.jpg', 'Wasp43b-finder-thumb.jpg')], help_text='Image with a clearly marked up target position', max_length=100, verbose_name='Finder chart thumbnail'),
        ),
        migrations.AlterField(
            model_name='event',
            name='illustration',
            field=models.CharField(blank=True, choices=[('illustration/planet_OGLE-TR-132b.jpg', 'planet_OGLE-TR-132b.jpg'), ('illustration/Hat-P-25b-finder-thumb2.jpg', 'Hat-P-25b-finder-thumb2.jpg'), ('illustration/planet_HAT-P-8b.jpg', 'planet_HAT-P-8b.jpg'), ('illustration/planet_HAT-P-11b.jpg', 'planet_HAT-P-11b.jpg'), ('illustration/planet_WASP-2b.jpg', 'planet_WASP-2b.jpg'), ('illustration/planet_HAT-P-25b.jpg', 'planet_HAT-P-25b.jpg'), ('illustration/planet_Qatar-1-b.jpg', 'planet_Qatar-1-b.jpg'), ('illustration/planet_TrES-3-b.jpg', 'planet_TrES-3-b.jpg'), ('illustration/planet_CoRoT-2b.jpg', 'planet_CoRoT-2b.jpg'), ('illustration/planet_GJ1214b.jpg', 'planet_GJ1214b.jpg'), ('illustration/planet_wasp43-b.jpg', 'planet_wasp43-b.jpg')], help_text='illustration for this event', max_length=100, verbose_name='illustration'),
        ),

    ]