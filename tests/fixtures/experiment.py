import vcr
import pytest
import cellengine


@pytest.fixture
def experiment(client):
    """Returns an experiment for testing"""
    with vcr.use_cassette('tests/cassettes/experiment.yaml'):
        experiment = cellengine.Experiment(name='test_experiment')
        return experiment

