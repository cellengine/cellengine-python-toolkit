import os
import json
import pytest
import responses
import cellengine
from cellengine import _helpers


base_url = os.environ.get('CELLENGINE_DEVELOPMENT',
                          'https://cellengine.com/api/v1/')


@responses.activate
def test_create_multiple_gates(gates):
    responses.add(responses.POST,
                  base_url+"experiments/5d86c71cb2fe73445a9286a7/gates",
                  status=201,
                  json=gates[0])
    responses.add(responses.POST,
                  base_url+"experiments/5d86c71cb2fe73445a9286a7/gates",
                  status=201,
                  json=gates[1])
    responses.add(responses.POST,
                  base_url+"experiments/5d86c71cb2fe73445a9286a7/gates",
                  status=201,
                  json=gates[2])
    all_gates = cellengine.Gate.create_gates('5d86c71cb2fe73445a9286a7', gates=gates)
    assert type(all_gates) is list
    assert all([type(gate) is cellengine.Gate for gate in all_gates])


# def test_update_gate():
#     pass


# def test_update_gate_family():
#     pass


# def test_delete_gate():
#     pass


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


@responses.activate
def test_create_rectangle_gate(experiment, rectangle_gate):
    """Test rectangle gate creation.

    Note that the returned object may not have values that match the request.
    This is because the returned object is built from a dict returned by a
    pytest fixture (intercepted by `responses`), not by the CE API.
    """
    responses.add(responses.POST,
                  base_url+"experiments/5d38a6f79fae87499999a74b/gates",
                  status=201,
                  json=rectangle_gate)
    rectangle_gate = experiment.create_rectangle_gate(x_channel="FSC-A",
                                                      y_channel="FSC-W",
                                                      name="my gate",
                                                      x1=60000,
                                                      x2=200000,
                                                      y1=75000,
                                                      y2=215000)
    gate_tester(rectangle_gate)
    assert rectangle_gate.model.rectangle.x1 == 60000
    assert rectangle_gate.model.rectangle.x2 == 200000
    assert rectangle_gate.model.rectangle.y1 == 75000
    assert rectangle_gate.model.rectangle.y2 == 215000


@responses.activate
def test_create_ellipse_gate(experiment, ellipse_gate):
    responses.add(responses.POST,
                  base_url+"experiments/5d38a6f79fae87499999a74b/gates",
                  status=201,
                  json=ellipse_gate)
    ellipse_gate = experiment.create_ellipse_gate(x_channel="FSC-A", y_channel="FSC-W",
                                  name="my gate", x=259441.51377370575, y=63059.462213950595, angle=0,
                                  major=120000, minor=70000)
    gate_tester(ellipse_gate)
    assert ellipse_gate.model.ellipse.center == [259441.51377370575, 63059.462213950595]
    assert ellipse_gate.model.ellipse.major == 113446.7481834943
    assert ellipse_gate.model.ellipse.minor == 70116.01916918601
    assert ellipse_gate.model.ellipse.angle == -0.16875182756633697


@responses.activate
def test_create_polygon_gate(experiment, polygon_gate):
    responses.add(responses.POST,
                  base_url+"experiments/5d38a6f79fae87499999a74b/gates",
                  status=201,
                  json=polygon_gate)
    polygon_gate = experiment.create_polygon_gate(x_channel="FSC-A",
                                                  y_channel="FSC-W",
                                                  name="my gate",
                                                  x_vertices=[1, 2, 3],
                                                  y_vertices=[4, 5, 6])
    gate_tester(polygon_gate)
    assert polygon_gate.model.polygon.vertices == [[59456.113402061856, 184672.1855670103],
                                                   [141432.10309278348, 181068.84536082475],
                                                   [82877.82474226804, 124316.23711340204],
                                                   [109002.0412371134, 63960.28865979381],
                                                   [44141.9175257732, 76571.97938144332],
                                                   [27926.886597938144, 107200.37113402062],
                                                   [10811.0206185567, 143233.77319587627],
                                                   [58555.278350515466, 145936.27835051547]]


@responses.activate
def test_create_range_gate(experiment, range_gate):
    responses.add(responses.POST,
                  base_url+"experiments/5d38a6f79fae87499999a74b/gates",
                  status=201,
                  json=range_gate)
    range_gate = experiment.create_range_gate(x_channel="FSC-A", name="my gate",
                                              x1=12.502,
                                              x2=95.102)
    gate_tester(range_gate)
    assert range_gate.model.range.x1 == 12.502
    assert range_gate.model.range.x2 == 95.102
    assert range_gate.model.range.y == 0.5



@responses.activate
def test_create_quadrant_gate(experiment, scalesets, quadrant_gate):
    responses.add(responses.GET,
                  base_url+"experiments/5d38a6f79fae87499999a74b/scalesets",
                  json=[scalesets])
    responses.add(responses.POST,
                  base_url+"experiments/5d38a6f79fae87499999a74b/gates",
                  status=201,
                  json=quadrant_gate)
    quadrant_gate = experiment.create_quadrant_gate(name='test_quadrant_gate',
                                                    x_channel='FSC-A',
                                                    y_channel='FSC-W',
                                                    x=160000,
                                                    y=200000)
    gate_tester(quadrant_gate)
    assert quadrant_gate.model.quadrant.x == 160000
    assert quadrant_gate.model.quadrant.y == 200000
    assert quadrant_gate.model.quadrant.angles == [1.5707963267948966, 3.141592653589793, 4.71238898038469, 0]
    assert quadrant_gate.model.gids == ['5db01cb2e4eb52e0c1047306',
                                        '5db01cb265909ddcfd6e2807',
                                        '5db01cb2486959d467563e08',
                                        '5db01cb21b8e42bc6499c609']
    assert quadrant_gate.names == ['my gate (UR)', 'my gate (UL)',
                                  'my gate (LL)', 'my gate (LR)']
    assert quadrant_gate.model.labels == [[1, 1], [-200, 1], [-200, -200], [1, -200]]


@responses.activate
def test_create_split_gate(experiment, scalesets, split_gate):
    responses.add(responses.GET,
                  base_url+"experiments/5d38a6f79fae87499999a74b/scalesets",
                  json=[scalesets])
    responses.add(responses.POST,
                  base_url+"experiments/5d38a6f79fae87499999a74b/gates",
                  status=201,
                  json=split_gate)
    split_gate = experiment.create_split_gate(x_channel="FSC-A",
                                              name="my gate",
                                              x=160000,
                                              y=100000)
    gate_tester(split_gate)
    assert split_gate.model.split.x == 160000
    assert split_gate.model.split.y == 1
    assert split_gate.model.gids == ['5db02aff9375ffe04e55b801', '5db02aff556563a0f01c7a02']
    assert split_gate.names == ['my gate (L)', 'my gate (R)']
    assert split_gate.model.labels == [[-199.9, 0.916], [0.9, 0.916]]
