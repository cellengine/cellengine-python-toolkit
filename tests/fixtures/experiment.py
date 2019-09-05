import vcr
import pytest
import cellengine
from conftest import fixture_vcr



@pytest.fixture
def experiment(client):
    """Returns an experiment for testing"""
    with fixture_vcr.use_cassette('tests/cassettes/experiment.yaml'):
        experiment = cellengine.Experiment(name='test_experiment')
        return experiment
