import cellengine
import pytest
from cellengine import Client
import vcr

@pytest.fixture
def client():
    '''Returns an authenticated Client object'''
    client = Client(username='gegnew', password='testpass1')
    return client



# @vcr.use_cassette('tests/http_cassettes/get-experiment.yml')
# def test_get_experiments(client):
#    '''Tests getting an experiment from api'''
#    client = Client(username='gegnew', password='foo4206969')
#    client.authenticate()
#    exp = client.get_experiment('160311-96plex-4dye')
#    assert exp.name == '160311-96plex-4dye'
#   TODO: more assertions here
#    print(object_properties)
#    #
