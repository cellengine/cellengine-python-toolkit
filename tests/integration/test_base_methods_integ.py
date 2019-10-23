import os
import vcr
import pytest
import cellengine
from cellengine import helpers as h


@pytest.mark.vcr()
class TestBaseMethods():
    with vcr.use_cassette('tests/cassettes/test_parse_fcs_file_args.yaml', record_mode='new_episodes'):
        client = cellengine.Client(username='gegnew', password='testpass1')

        def method_tester(self, res):
            """Generalize tests for common response fields"""
            assert res['_id'] == '5d38a6f79fae87499999a74b'
            '5d38a6f79fae87499999a74b'
            assert res['name'] == 'test_experiment'
            assert res['created'] == '2019-07-24T18:44:07.520Z'


        @pytest.mark.vcr()
        def test_base_get(self):
            res = h.base_get('experiments/5d38a6f79fae87499999a74b')
            self.method_tester(res)


        @pytest.mark.vcr()
        def test_base_create(self, client):
            """Test base create for an instantiated data class response"""
            res = h.base_create(cellengine.Experiment, url='experiments', expected_status=201, json={'name': 'Test Experiment'})
            assert type(res) is cellengine.Experiment
            assert res.name == 'Test Experiment'


        @pytest.mark.vcr()
        def test_base_update(self, client):
            """Will fail the first time, as it needs to build the cassette. Passes thereafter."""
            h.base_update('experiments/5d64abe2ca9df61349ed8e78',
                          body={
                              'name': 'newname',
                              'locked': True,
                              'fullName': 'Primity Bio'
                          })

            with vcr.use_cassette('tests/cassettes/TestBaseMethods.test_base_update.yaml') as cass:
                req = cass.requests[0]
                assert req.method == 'PATCH'
                assert 'newname' in req.body.decode()
