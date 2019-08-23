import cellengine
import pytest
from cellengine import Client
import vcr


@pytest.fixture
def client():
    '''Returns an authenticated Client object'''
    client = Client(username='gegnew', password='testpass1')
    return client


@pytest.fixture
def exp(client):
    '''Returns an experiment for testing'''
    exp = cellengine.Experiment(name='160311-96plex-4dye')
    return exp


@vcr.use_cassette('tests/http_cassettes/get-experiment.yml')
def test_get_experiments(client):
    '''Tests getting an experiment from api'''
    exp = cellengine.Experiment('160311-96plex-4dye')
    assert exp.name == '160311-96plex-4dye'
#   TODO: more assertions here
    # assert set(object_properties).issubset(exp._properties.keys())
    assert exp.name == '160311-96plex-4dye'
    assert exp._id == '5d38a6f79fae87499999a74b'
    assert exp.query == 'name'
    assert type(exp._properties) is dict
    # assert type(exp.session) is requests_toolbelt.sessions.BaseUrlSession


@vcr.use_cassette('tests/http_cassettes/get_fcsfile.yml')
def test_list_fcsfile(exp):
    '''Tests listing files in an experiment'''
    files = exp.files
#   TODO: more assertions here
    assert type(files) is list


@vcr.use_cassette('tests/http_cassettes/list-compensations.yml')
def test_list_compensations(exp):
    '''Tests retrieval of list of compensations from API'''
    comps = exp.compensations
#   TODO: find an .fcs file for testing that has compensations
    assert(type(comps)) is list
