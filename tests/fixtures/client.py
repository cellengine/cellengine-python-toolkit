import vcr
import pytest
import cellengine


@pytest.fixture
def client():
    """Returns an authenticated Client object
    This fixture should be passed to all other fixtures to ensure
    that tests run on an authenticated session of CellEngine."""
    with vcr.use_cassette('tests/cassettes/client.yaml'):
        client = cellengine.Client(username='gegnew', password='testpass1')
        return client
