# Basic test to begin unit testing adventure

# Import pytest for testing 
import pytest

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 5