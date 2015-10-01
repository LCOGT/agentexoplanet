#################################################################################
############################# TEST IS NON FUNCTIONAL ############################
#DO NOT USE FOR TESTING: FAILS BECAUSE OF PROBLEMS IMPLEMENTING MOCK/FACTORY BOY#
#################################################################################

# Test has issues when encountering DataSource.objects.filter() in function under
# test (found at the top of datareduc.py). The factory created (DataSourceFactory)
# has problems with .objects - Python returns that DataSourceFactory has no
# attribute 'objects'

'''
# Import pytest
import pytest

# Import unittest
import unittest

# Import factories to use in place of models
import factories

# Import modules required for some aspects of tests
import random
import time

# Import Mock to allow for function calls
import mock

# Import views and models required
from agentex.datareduc import calibrator_data


class TestDataReduction(unittest.TestCase):

################################################################################
############################ Testing calibrator_data ###########################
################################################################################

    # @mock.patch allows the first argument to be replaced by the second argument.
    # In this case, the 'real' models DataSource, Datapoint and Decision are
    # replaced by factories emulating their behaviour from factories.py. These are
    # then used instead of the first argument whenever the first argument is
    # called.
    @mock.patch('agentex.datareduc.DataSource', factories.DataSourceFactory.build())
    @mock.patch('agentex.datareduc.Datapoint', factories.DatapointFactory.build())
    @mock.patch('agentex.datareduc.Decision', factories.DecisionFactory.build())
    def test_calibrator_data(self):

        calid = 22
        code = 'trenzalore'

        output = calibrator_data(calid,code)

        assert type(output[0])==type([])
'''
