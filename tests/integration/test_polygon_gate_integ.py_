import pytest
import numpy
from cellengine import helpers
from test_gates_integ import gate_tester


@pytest.mark.vcr()
def test_create_polygon_gate(experiment):
    """Test for correct creation of a polygon gate."""
    resp = experiment.create_polygon_gate(x_channel='FSC-W',
                                               y_channel='FSC-A',
                                               name='test_polygon_gate',
                                               x_vertices=[1, 2, 3],
                                               y_vertices=[4, 5, 6]
                                               )
    gate_tester(resp)
    assert resp.experiment_id == experiment._id
    assert resp.x_channel == 'FSC-W'
    assert resp.y_channel == 'FSC-A'
    assert resp.name == 'test_polygon_gate'
    assert resp.model.label == [numpy.mean([1, 2, 3]),
                                numpy.mean([4, 5, 6])]
    assert resp.model.polygon.vertices == [[1, 4], [2, 5], [3, 6]]
    assert resp.model.locked is False
    assert resp.type == 'PolygonGate'
    assert resp.tailored_per_file is False

