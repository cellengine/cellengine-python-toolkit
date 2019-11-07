import os
import vcr
import pytest
import cellengine
from conftest import scrub_client_request
from cellengine import _helpers

# vcr instance for the client object
client_vcr = vcr.VCR(
    before_record_response=scrub_client_request(),
    filter_headers=['Cookie'],
    filter_query_parameters=['token']
)


@pytest.fixture(scope='session', autouse=True)
def setup_teardown(request, make_new_cassettes):

    def fin():
        print('\n Tearing down test experiment.')
        _helpers.session.delete('experiments/{0}'.format(_id))

    if make_new_cassettes is False:
        pass
    else:
        print('Deleting old files.')
        for file in os.listdir('tests/cassettes'):
            os.remove(os.path.join('tests/cassettes', file))
        print('Setting up experiment.')
        res = _helpers.session.post('experiments', json={'name': 'pytest'})
        _id = res.json()['_id']
        _helpers.session.post('experiments/{0}/fcsfiles'.format(_id),
                              files={'Acea - Novocyte.fcs':
                                     open('tests/fcsfiles/Acea - Novocyte.fcs',
                                          'rb')})

        request.addfinalizer(fin)


@pytest.fixture(scope='session', autouse=True)
def client():
    """Returns an authenticated Client object
    This fixture should be passed to all other fixtures to ensure
    that tests run on an authenticated session of CellEngine."""
    with client_vcr.use_cassette('tests/cassettes/client.yaml'):
        client = cellengine.Client(username='gegnew', password='testpass1')
        return client
