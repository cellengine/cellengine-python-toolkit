import pytest
import cellengine


@pytest.mark.vcr()
def test_get_experiment(client):
    """Tests getting an experiment from api"""
    exp = cellengine.Experiment('test_experiment')
    assert exp.name == 'test_experiment'
#   TODO: more assertions here
    # assert set(object_properties).issubset(exp._properties.keys())
    assert exp.name == 'test_experiment'
    assert exp._id == '5d38a6f79fae87499999a74b'
    assert type(exp._properties) is dict
    # assert type(exp.session) is requests_toolbelt.sessions.BaseUrlSession


@pytest.mark.vcr()
def test_list_fcsfile(experiment):
    '''Tests listing files in an experiment'''
    files = experiment.files
#   TODO: more assertions here
    assert type(files) is list


@pytest.mark.vcr()
def test_list_compensations(experiment):
    '''Tests retrieval of list of compensations from API'''
    comps = experiment.compensations
#   TODO: find an .fcs file for testing that has compensations
    assert type(comps) is list
