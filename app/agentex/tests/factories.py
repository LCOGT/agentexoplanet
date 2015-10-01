import factory
import factory.django

import agentex.models as models

import datetime
import random

'''
This file contains all of the factories used to emulate/override the
models found in models.py for testing purposes.
'''

class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Event
    # This class is essential. It allows factory_boy to generate the correct model
    # in order to duplicate correctly

    # These are replacement objects to take the place of the originals found in
    # the original models
    name = 'trenzalore'
    finder = long(random.randint(0,500))

class DataSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DataSource

    id = long(random.randint(0,50))
    timestamp = datetime.datetime.now
    # factory.SubFactory is the equivalent of a ForeignKey and allows the
    # individual factories to link to one another much in the way that
    # ForeignKey allows
    event = factory.SubFactory(EventFactory)

class CatSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CatSource

    id = random.randint(0,50)
    name = 'Raxacoricofallapatorius'
    data = factory.SubFactory(DataSourceFactory)

class DatapointFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Datapoint

    data = factory.SubFactory(DataSourceFactory)
    source = factory.SubFactory(CatSourceFactory)

class DecisionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Decision

    source = factory.SubFactory(CatSourceFactory)
    planet = factory.SubFactory(EventFactory)
    value = float(random.randint(0,500))
