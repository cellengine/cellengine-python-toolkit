import os
import json

import pytest
import vcr
from cellengine import _helpers as h


def method_tester(res):
    """Generalize tests for common response fields"""
    assert res['_id'] == '5d38a6f79fae87499999a74b'
    '5d38a6f79fae87499999a74b'
    assert res['name'] == 'test_experiment'
    assert res['created'] == '2019-07-24T18:44:07.520Z'


@pytest.mark.vcr()
def test_base_get():
    res = h.base_get('experiments/5d38a6f79fae87499999a74b')
    method_tester(res)


@pytest.mark.vcr()
def test_base_get_bytes():
    """Test base get for a bytes object response"""
    res = h.base_get('experiments/5d38a6f79fae87499999a74b/fcsfiles/5d38a719b027474998027903.fcs')
    assert res.ok
    assert res.encoding is None
    assert type(res.content) is bytes


# with vcr.use_cassette('tests/cassettes/test_base_create.yml', method="POST") as cass:
@pytest.mark.vcr()
def test_base_create():
    """This test is a bit touchy; if you ever have to delete this
    cassette, make sure you edit the test _id below, changing it to
    whatever is in the .yml in http_cassettes/

    VCR doesn't seem to be preventing this from going to the API
    """
    h.base_create('experiments', body={'name': 'Test Experiment'})

    with vcr.use_cassette('tests/cassettes/test_base_create.yaml') as cass:
        res = json.loads(cass.responses[0]['body']['string'])
        assert res['name'] == 'Test Experiment'
        assert res['_id'] == '5d7007f5f0b5ec141f6e385f'


@pytest.mark.vcr()
def test_base_update():
    h.base_update('experiments/5d64abe2ca9df61349ed8e78',
                  body={
                      'name': 'newname',
                      'locked': True,
                      'fullName': 'Primity Bio'
                  })

    with vcr.use_cassette('tests/cassettes/test_base_update.yaml') as cass:
        req = cass.requests[0]
        # res = json.loads(cass.responses[1]['body']['string'])
        assert req.method == 'PATCH'
        assert 'newname' in req.body.decode()


@pytest.mark.vcr()
def test_base_delete(client):
    """Tests the base delete method.
    This test depends on (a) the client fixture being valid for
    this experiment and (b) the test existing for that client
    when the cassette is made. If you delete either client.yaml
    or test_base_delete.yaml, you must delete the other. Then
    the two cassettes will save properly.
    """
    _id = '5d7007f5f0b5ec141f6e385f'
    with vcr.use_cassette('tests/cassettes/test_base_delete.yaml') as cass:
        h.base_delete('experiments/{0}'.format(_id))
        req = cass.requests[0]
        res = cass.responses[0]
        assert req.method == 'DELETE'
        assert req.path == '/api/v1/experiments/{0}'.format(_id)
        assert res['status']['code'] == 204


def test_base_delete_mock(requests_mock):
    """Mocked version of test_base_delete"""
    BASE_URL = os.environ.get('CELLENGINE_DEVELOPMENT', 'https://cellengine.com/api/v1/')
    requests_mock.delete('http://localhost:3000/api/v1/test-delete',
                         status_code=204)
    resp = h.base_delete('test-delete')
    assert resp.status_code == 204
    assert resp.request.method == 'DELETE'
    assert resp.request.url == BASE_URL+'test-delete'
