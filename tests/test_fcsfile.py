import pytest
from cellengine import Client
import vcr

@pytest.fixture
def client():
    '''Returns an authenticated Client object'''
    client = Client(username='gegnew', password='testpass1')
    return client

# files = exp.files(experiment_id='5d38a6f79fae87499999a74b', name='Specimen_001_A9_A09.fcs')

