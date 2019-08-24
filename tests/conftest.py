import vcr
import pytest
import cellengine

"""
Run tests with ``python -m pytest``.

Fixtures are defined in cellengine-python-toolkit/tests/tests/fixtures.
You can write new fixtures in new files here, or in existing .py files.
Fixtures in the ..tests/fixtures folder can use other fixtures in that folder.

Fixtures must be imported below using the ``pytest_plugins`` list.
"""


pytest_plugins = [
    "fixtures.client",
    "fixtures.experiment"
]

# @pytest.fixture
# def client():
#     """Returns an authenticated Client object
#     This fixture should be passed to all other fixtures to ensure
#     that tests run on an authenticated session of CellEngine."""
#     with vcr.use_cassette('tests/cassettes/client.yaml'):
#         client = cellengine.Client(username='gegnew', password='testpass1')
#         return client


# @pytest.fixture
# def experiment(client):
#     """Returns an experiment for testing"""
#     with vcr.use_cassette('tests/cassettes/experiment.yaml'):
#         experiment = cellengine.Experiment(name='test_experiment')
#         return experiment
