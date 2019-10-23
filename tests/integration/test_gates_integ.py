import vcr
import numpy
import pytest
import cellengine
from cellengine import helpers


def gate_tester(instance):
    """Generalize tests for shared gate fields"""
    assert type(instance) is cellengine.Gate
    assert hasattr(instance, 'experiment_id')
    assert hasattr(instance, 'name')
    assert hasattr(instance, 'type')
    assert hasattr(instance, 'gid')
    assert hasattr(instance, 'x_channel')
    assert hasattr(instance, 'y_channel')
    assert hasattr(instance, 'tailored_per_file')
    assert hasattr(instance, 'fcs_file_id')
    assert hasattr(instance, 'parent_population_id')
    assert hasattr(instance, 'model')


@pytest.mark.vcr()
def test_parse_fcs_file_args():
    """Test various fcs file arg combinations"""
    with vcr.use_cassette('tests/cassettes/test_parse_fcs_file_args.yaml', record_mode='new_episodes'):

        # fcs_file and fcs_file_id defined
        with pytest.raises(ValueError):
            resp = cellengine.Gate.create_rectangle_gate('5d38a6f79fae87499999a74b',
                                                         'FSC-A', 'FSC-W', 'fcs_rect_gate',
                                                         x1=1, x2=2, y1=3, y2=4,
                                                         fcs_file='Specimen_001_A1_A01.fcs',
                                                         fcs_file_id='5d38a7159fae87499999a74e',
                                                         tailored_per_file=True)

            # tailored_per_file is False
            resp = cellengine.Gate.create_rectangle_gate('5d38a6f79fae87499999a74b',
                                                         'FSC-A', 'FSC-W', 'fcs_rect_gate',
                                                         x1=1, x2=2, y1=3, y2=4,
                                                         fcs_file='Specimen_001_A1_A01.fcs',
                                                         tailored_per_file=False)
            assert resp.tailored_per_file is False

            # fcs_file_id is None and fcs_file is None
            resp = cellengine.Gate.create_rectangle_gate('5d38a6f79fae87499999a74b',
                                                         'FSC-A', 'FSC-W', 'fcs_rect_gate',
                                                         x1=1, x2=2, y1=3, y2=4)
            assert resp.fcs_file_id is None

            # fcs_file_id is None and fcs_file is None
            resp = cellengine.Gate.create_rectangle_gate('5d38a6f79fae87499999a74b',
                                                         'FSC-A', 'FSC-W', 'fcs_rect_gate',
                                                         x1=1, x2=2, y1=3, y2=4)
            assert resp.fcs_file_id is None

            # create global tailored gate
            global_gid = helpers.generate_id()
            # global_gid = '5d8e68ccda9be554bc83b903'
            resp = cellengine.Gate.create_rectangle_gate('5d38a6f79fae87499999a74b',
                                                         'FSC-A', 'FSC-W', 'fcs_rect_gate',
                                                         x1=1, x2=2, y1=3, y2=4,
                                                         tailored_per_file=True,
                                                         gid=global_gid)
            assert resp.tailored_per_file is True
            assert resp.gid == global_gid

            # specify fcs_file
            resp = cellengine.Gate.create_rectangle_gate('5d38a6f79fae87499999a74b',
                                                         'FSC-A', 'FSC-W', 'fcs_rect_gate',
                                                         x1=1, x2=2, y1=3, y2=4,
                                                         fcs_file='Specimen_001_A1_A01.fcs',
                                                         tailored_per_file=True,
                                                         gid=global_gid)
            assert resp.fcs_file_id == '5d38a715b0274749980278e9'
            assert resp.gid == global_gid

            # specify fcs_file_id
            resp = cellengine.Gate.create_rectangle_gate('5d38a6f79fae87499999a74b',
                                                         'FSC-A', 'FSC-W', 'fcs_rect_gate',
                                                         x1=1, x2=2, y1=3, y2=4,
                                                         fcs_file_id='5d38a7159fae87499999a751',
                                                         tailored_per_file=True,
                                                         gid=global_gid)
            assert resp.fcs_file_id == '5d38a7159fae87499999a74e'
            assert resp.gid == global_gid
            assert resp.name == 'Specimen_001_A2_A02.fcs'

            # # delete all created gates
            # for item in helpers.session.get(f"experiments/5d38a6f79fae87499999a74b/gates").json():
            #     _id = item['_id']
            #     name = item['name']
            #     if 'fcs_rect_gate' in name:
            #         cellengine.helpers.session.delete(f"experiments/5d38a6f79fae87499999a74b/gates/{_id}")


