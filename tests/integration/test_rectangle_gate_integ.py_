import pytest
import numpy
from cellengine import helpers
from test_gates_integ import gate_tester

@pytest.mark.vcr()
def test_create_rectangle_gate(experiment):
    """Test for correct creation of a rectangle gate."""
    resp = experiment.create_rectangle_gate(name='test_rect_gate',
                                                 x_channel='FSC-W',
                                                 y_channel='FSC-A',
                                                 x1=60000,
                                                 x2=200000,
                                                 y1=75000,
                                                 y2=215000)
    gate_tester(resp)
    assert resp.experiment_id == experiment._id
    assert resp.x_channel == 'FSC-W'
    assert resp.y_channel == 'FSC-A'
    assert resp.name == 'test_rect_gate'
    assert resp.model.label == [numpy.mean([60000, 200000]),
                                numpy.mean([75000, 215000])]
    assert resp.model.rectangle.x1 == 60000
    assert resp.model.rectangle.x2 == 200000
    assert resp.model.rectangle.y1 == 75000
    assert resp.model.rectangle.y2 == 215000
    assert resp.model.locked is False
    assert resp.type == 'RectangleGate'
    assert resp.tailored_per_file is False

    helpers.session.delete(f"experiments/{experiment._id}/gates/{resp._id}")


@pytest.mark.vcr()
def test_create_global_gate(experiment):
    """Test creation with fcs_file_id specified."""
    resp = experiment.create_rectangle_gate(x_channel='FSC-W',
                                            y_channel='FSC-A', name='fcs_global_gate',
                                            x1=60000, x2=200000, y1=75000, y2=215000,
                                            tailored_per_file=True,
                                            locked=False,
                                            create_population=False)
    gate_tester(resp)
    assert resp.experiment_id == experiment._id
    assert resp.x_channel == 'FSC-W'
    assert resp.y_channel == 'FSC-A'
    assert resp.name == 'fcs_global_gate'
    assert bool(helpers.ID_REGEX.match(resp.gid)) is True
    assert resp.model.label == [numpy.mean([60000, 200000]),
                                numpy.mean([75000, 215000])]
    assert resp.model.rectangle.x1 == 60000
    assert resp.model.rectangle.x2 == 200000
    assert resp.model.rectangle.y1 == 75000
    assert resp.model.rectangle.y2 == 215000
    assert resp.model.locked is False
    assert resp.parent_population_id is None
    assert resp.type == 'RectangleGate'
    assert resp.tailored_per_file is True
