# Test to verify database read and writes correctly

# Import TestCase
from django.test import TestCase, Client

# Import Target from models
#from agentex.models import Target

# Class for testing whether database is written to correctly
class TestData(TestCase):

    def setUp(self):
        self.client = Client()

    def test_data(self):
        
        # Creates dummy entry in database
        dummy = models.Target.objects.create(name="Dummy-1b")
        
        retrieve = models.Target.objects.get(name="Dummy-1b")
        self.assertEqual(dummy, retrieve)

