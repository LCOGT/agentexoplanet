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
'''

class TestCalibratorData(TestCase):

    def setUp(self):
        self.client = Client()

    def test_calibrator_data(self):

        calid = [[1.0027368135066828, 1.0132907205041479, 0.96722679141680545, 0.99456124655374001, 0.9678167506492511, 0.97059108507246183, 0.97544481338508437, 0.97548031354646791, 0.98628376039206656, 0.98063447405450066, 0.99786942830874736, 1.0166881513291954, 1.0021880949344202]]
        code = {'dip': 0, 'total': 2, 'done': 1}

        calibrator = calibrator_data(calid,code)
        self.assertNotEqual(calibrator, [])

'''
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