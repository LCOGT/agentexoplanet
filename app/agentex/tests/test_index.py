# Test to verify homepage loads correctly

# Import TestCase from unittest (unsure if really required)
from django.test import TestCase

# Import reverse
from django.core.urlresolvers import reverse

# Import Client (acts as a dummy browser allowing testing)
from django.test import Client

'''
class TestPage(TestCase):

    #def setUp(self):
    #    self.client = Client()

    # Define function for test
    def test_page(self):
        #url = reverse('index.html')
        response = self.client.get(reverse('index'))
        #self.assertValidResponse(response)
        self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, 'index.html')
'''
