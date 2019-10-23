import vcr
import pytest
import cellengine
from conftest import fixture_vcr


@pytest.fixture
def gate(client):
    """Returns a gate for testing"""
    with fixture_vcr.use_cassette('tests/cassettes/gate.yaml'):
        experiment = cellengine.Experiment(name='test_experiment')
        gate = experiment.gates[-1]
        return gate
