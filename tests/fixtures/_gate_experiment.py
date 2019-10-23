import os
import pytest
import cellengine
from conftest import fixture_vcr
from cellengine import _helpers


@pytest.fixture(scope='session')
@pytest.mark.vcr(record_mode='once')
def gate_experiment(request, client):
    """Spin up an experiment with a file for testing, tear down afterwards"""
    with fixture_vcr.use_cassette('tests/cassettes/spinup_experiment.yaml'):
        res = client._session.post('experiments', json={'name': 'sdk'})
        _id = res.json()['_id']
        file_res = _helpers.session.post(f'experiments/{_id}/fcsfiles', files={'Acea - Novocyte.fcs': open('tests/fcsfiles/Acea - Novocyte.fcs', 'rb')})
        gate_experiment = cellengine.Experiment(id=_id)

    # TODO: figure out some logic about when to make this request
    def fin():
        print('Tearing down test experiment.')
        d = client._session.delete(f'experiments/{_id}')

    if os.path.isfile('tests/cassettes/spinup_experiment.yaml'):
        pass
    else:
        request.addfinalizer(fin)

    return gate_experiment
