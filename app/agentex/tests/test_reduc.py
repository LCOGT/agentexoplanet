# Import TestCase from unittest 
from django.test import TestCase, Client

# Import reverse
from django.core.urlresolvers import reverse

# Import Client (acts as a dummy browser allowing testing)
from django.test import client

# Import Mock to allow for function calls
from mock import Mock, patch

# Import view required
from agentex.datareduc import *

'''
Mock objects live here.
'''

def mocking_calave():
    cals, sc, bg, stamps, ids, cats = 1, 1, 1, 1, 1, 1
    return cals,sc,bg,stamps,ids,cats

'''
Actual tests live here.


class TestCalibratorData(TestCase):

    def setUp(self):
        self.client = Client()

    def test_calibrator_data(self):

        calid = None
        code = 'testing'

        d, t, p = calibrator_data(calid,code)
        self.assertNotEqual(calibrator, [])

class TestAverageCombine(TestCase):

    def setUp(self):
        self.client = Client()

    def test_average_combine(self):


class TestPhotometry(TestCase):
    
    @patch('agentex.datareduc.calibrator_averages', side_effect=mocking_calave)
    
    def test_photometry(self, mocking_calave):

        photom = photometry(code=0,person=None)
        cal_ave = mocking_calave()
 
        self.assertNotEqual(cal_ave, photom)
'''