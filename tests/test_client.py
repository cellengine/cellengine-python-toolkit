import cellengine
import pytest
from cellengine import Client
# from conftest import my_vcr


@pytest.fixture
def object_properties():
    '''Property keys in every object'''
    return ['_id', 'name', '__v']


def mock_test_client(username=None, password=None, token=None):
    return {'token': 's:U4S28.kr7KyZdni/XX9ac',
            'userId': '5d366077a1789f7d6653075c',
            'admin': True,
            'flags': {},
            'authenticated': True}


# def test_client(monkeypatch):
#     client = Client(username='gegnew', password='foo4206969')
#     monkeypatch.setattr(client, 'authenticate', mock_test_client)
#     response = client
#     assert response['userId'] == '5d366077a1789f7d6653075c', 'user who started instance'
#     assert response['token'] == 's:U4S28.kr7KyZdni/XX9ac', 'user who started instance'
#     assert response['admin'] is True
#     assert response['flags'] == {}

@pytest.mark.vcr()
def test_list_experiments(client):
    '''Tests listing experiments from api'''
    exps = client.experiments
#   TODO: more assertions here
    assert type(exps) is list
    assert type(exps[0]) is cellengine.experiment.Experiment
