# Test to verify photometry works correctly

# Import TestCase from unittest (unsure if really required)
from django.test import TestCase

# Import reverse
from django.core.urlresolvers import reverse

# Import Client (acts as a dummy browser allowing testing)
from django.test import client

# Import Mock to allow for function calls
from mock import Mock

# Import view required
from agentex.views import photometry, calibrator_averages

class TestPhotometry(TestCase):

    def test_photometry(self):

        # Takes the view photometry from views.py
        self.client.get(views.photometry)


        self.assertNotEqual(calibrator_averages(code,person,progress), (cals,normcals,list(sc),list(bg),dates,stamps,indexes,cats))
