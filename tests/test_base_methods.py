import vcr
import pytest
import json
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
        assert res['_id'] == '5d656ec3c61acb1589769209'


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
    h.base_delete('experiments/5d64abe5cbc120134a70e2a3')
    with vcr.use_cassette('tests/cassettes/test_base_delete.yaml') as cass:
        req = cass.requests[0]
        res = cass.responses[0]
        assert req.method == 'DELETE'
        assert req.path == '/api/v1/experiments/5d64abe5cbc120134a70e2a3'
        assert res['status']['code'] == 204
