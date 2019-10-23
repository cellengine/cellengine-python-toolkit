import cellengine
import pytest


def test_client(client):
    """Test Client properties"""
    assert client.username == 'gegnew'
    assert client.password == 'testpass1'
    assert client._session is not None


@pytest.mark.vcr()
def test_list_experiments(client):
    """Tests listing experiments from api"""
    exps = client.experiments
#   TODO: more assertions here
    assert type(exps) is list
    assert type(exps[0]) is cellengine.experiment.Experiment
