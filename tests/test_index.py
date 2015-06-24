# Test to verify homepage loads correctly

# Import pytest
import pytest

# Define function 
def homepagetest(self):
    response = self.c.get('/agentex/templates/index.html')
    self.assertEqual(response.status_code, 200)