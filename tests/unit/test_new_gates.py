import os
from abc import ABC
import json
import pytest
import responses
import cellengine
from cellengine import _helpers
from cellengine import gate

base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


def gate_tester(instance):
    """Generalize tests for shared gate fields"""
    # assert type(instance) is cellengine.Gate
    assert hasattr(instance, "experiment_id")
    assert hasattr(instance, "name")
    assert hasattr(instance, "type")
    assert hasattr(instance, "gid")
    assert hasattr(instance, "x_channel")
    assert hasattr(instance, "y_channel")
    assert hasattr(instance, "tailored_per_file")
    assert hasattr(instance, "fcs_file_id")
    assert hasattr(instance, "parent_population_id")
    assert hasattr(instance, "model")


def test_init_gate(polygon_gate):
    """Test instantiating a gate object a correct dict of properties"""
    g = cellengine.PolygonGate(properties=polygon_gate)
    gate_tester(g)
    assert g.experiment_id == "5d38a6f79fae87499999a74b"
    assert g.x_channel == "FSC-A"
    assert g.y_channel == "FSC-H"
    assert g.name == "poly_gate"
    assert g.model == {
        "label": [59456.113402061856, 193680.53608247422],
        "locked": False,
        "polygon": {
            "vertices": [
                [59456.113402061856, 184672.1855670103],
                [141432.10309278348, 181068.84536082475],
                [82877.82474226804, 124316.23711340204],
                [109002.0412371134, 63960.28865979381],
                [44141.9175257732, 76571.97938144332],
                [27926.886597938144, 107200.37113402062],
                [10811.0206185567, 143233.77319587627],
                [58555.278350515466, 145936.27835051547],
            ]
        },
    }


@responses.activate
def test_create_one_gate(rectangle_gate):
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=201,
        json=rectangle_gate,
    )
    g = gate.Gate.create(rectangle_gate)
    gate_tester(g)


@responses.activate
def test_create_multiple_gates(rectangle_gate):
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=201,
        json=[rectangle_gate, rectangle_gate],
    )
    gates = gate.Gate.create([rectangle_gate, rectangle_gate])
    gate_tester(gates[0])
    gate_tester(gates[1])


@pytest.fixture
def bad_gate():
    bad_gate = {
        "__v": 0,
        "experimentId": "5d38a6f79fae87499999a74b",
        # "name": "my gate",
        "type": "PolygonGate",
        # "gid": "5dc6e4514855ff5d3d041d03",
        "xChannel": "FSC-A",
        "yChannel": "FSC-W",
        "parentPopulationId": None,
        "model": {
            "polygon": {"vertices": [[1, 4], [2, 5], [3, 6]]},
            "label": [2, 5],
            "locked": False,
        },
        "_id": "5dc6e451447b66af32faba31",
        "fcsFileId": None,
        "tailoredPerFile": False,
        "names": [],
    }
    return bad_gate


@responses.activate
def test_create_gate_with_bad_params(bad_gate):
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=400,
        json={"error": '"gid" is required.'},
    )
    with pytest.raises(RuntimeError):
        g = gate.Gate.create(bad_gate)
        g.post()


@responses.activate
def test_create_polygon_gate(polygon_gate):
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=201,
        json=polygon_gate,
    )
    g = gate.PolygonGate.create(
        experiment_id="5d38a6f79fae87499999a74b",
        x_channel="FSC-A",
        y_channel="FSC-H",
        name="poly_gate",
        x_vertices=[1, 2, 3],
        y_vertices=[4, 5, 6],
    )
    gate_tester(g)
    assert g.experiment_id == "5d38a6f79fae87499999a74b"
    assert g.x_channel == "FSC-A"
    assert g.y_channel == "FSC-H"
    assert g.name == "poly_gate"
    assert g.model == {
        "label": [59456.113402061856, 193680.53608247422],
        "locked": False,
        "polygon": {
            "vertices": [
                [59456.113402061856, 184672.1855670103],
                [141432.10309278348, 181068.84536082475],
                [82877.82474226804, 124316.23711340204],
                [109002.0412371134, 63960.28865979381],
                [44141.9175257732, 76571.97938144332],
                [27926.886597938144, 107200.37113402062],
                [10811.0206185567, 143233.77319587627],
                [58555.278350515466, 145936.27835051547],
            ]
        },
    }


# # def test_fcs_file_and_fcs_file_id_defined(experiment, experiments, gates):


# # def test_create_multiple_gate():
# #     g = gate.Gate.create(["PolygonGate", "PolygonGate"])
# #     assert g[0].model["locked"] is False


# # def test_gate_properties():
# #     g = gate.Gate.create("PolygonGate")
# #     gate_tester(g)


# @responses.activate
# def test_create_rectangle_gate(experiment, rectangle_gate):
#     """Test rectangle gate creation.

#     Note that the returned object may not have values that match the request.
#     This is because the returned object is built from a dict returned by a
#     pytest fixture (intercepted by `responses`), not by the CE API.
#     """
#     responses.add(
#         responses.POST,
#         base_url + "experiments/5d38a6f79fae87499999a74b/gates",
#         status=201,
#         json=rectangle_gate,
#     )

#     g = gate.PolygonGate.create(
#         experiment_id="5d38a6f79fae87499999a74b",
#         x_channel="FSC-A",
#         y_channel="FSC-W",
#         name="my gate",
#         x1=60000,
#         x2=200000,
#         y1=75000,
#         y2=215000,
#     )
#     gate_tester(g)
#     assert g.model.rectangle.x1 == 60000
#     assert g.model.rectangle.x2 == 200000
#     assert g.model.rectangle.y1 == 75000
#     assert g.model.rectangle.y2 == 215000


# # @responses.activate
# # def test_create_multiple_gates(gates):
# #     responses.add(responses.POST,
# #                   base_url+"experiments/5d86c71cb2fe73445a9286a7/gates",
# #                   status=201,
# #                   json=gates[0])
# #     responses.add(responses.POST,
# #                   base_url+"experiments/5d86c71cb2fe73445a9286a7/gates",
# #                   status=201,
# #                   json=gates[1])
# #     responses.add(responses.POST,
# #                   base_url+"experiments/5d86c71cb2fe73445a9286a7/gates",
# #                   status=201,
# #                   json=gates[2])
# #     all_gates = cellengine.Gate.create_gates('5d86c71cb2fe73445a9286a7', gates=gates)
# #     assert type(all_gates) is list
# #     assert all([type(gate) is cellengine.Gate for gate in all_gates])


# # # def test_update_gate():
# # #     pass


# # # def test_update_gate_family():
# # #     pass


# # # def test_delete_gate():
# # #     pass


# # @responses.activate
# # def test_create_ellipse_gate(experiment, ellipse_gate):
# #     responses.add(responses.POST,
# #                   base_url+"experiments/5d38a6f79fae87499999a74b/gates",
# #                   status=201,
# #                   json=ellipse_gate)
# #     ellipse_gate = experiment.create_ellipse_gate(x_channel="FSC-A", y_channel="FSC-W",
# #                                   name="my gate", x=259441.51377370575, y=63059.462213950595, angle=0,
# #                                   major=120000, minor=70000)
# #     gate_tester(ellipse_gate)
# #     assert ellipse_gate.model.ellipse.center == [259441.51377370575, 63059.462213950595]
# #     assert ellipse_gate.model.ellipse.major == 113446.7481834943
# #     assert ellipse_gate.model.ellipse.minor == 70116.01916918601
# #     assert ellipse_gate.model.ellipse.angle == -0.16875182756633697


# # @responses.activate
# # def test_create_polygon_gate(experiment, polygon_gate):
# #     responses.add(responses.POST,
# #                   base_url+"experiments/5d38a6f79fae87499999a74b/gates",
# #                   status=201,
# #                   json=polygon_gate)
# #     polygon_gate = experiment.create_polygon_gate(x_channel="FSC-A",
# #                                                   y_channel="FSC-W",
# #                                                   name="my gate",
# #                                                   x_vertices=[1, 2, 3],
# #                                                   y_vertices=[4, 5, 6])
# #     gate_tester(polygon_gate)
# #     assert polygon_gate.model.polygon.vertices == [[59456.113402061856, 184672.1855670103],
# #                                                    [141432.10309278348, 181068.84536082475],
# #                                                    [82877.82474226804, 124316.23711340204],
# #                                                    [109002.0412371134, 63960.28865979381],
# #                                                    [44141.9175257732, 76571.97938144332],
# #                                                    [27926.886597938144, 107200.37113402062],
# #                                                    [10811.0206185567, 143233.77319587627],
# #                                                    [58555.278350515466, 145936.27835051547]]


# # @responses.activate
# # def test_create_range_gate(experiment, range_gate):
# #     responses.add(responses.POST,
# #                   base_url+"experiments/5d38a6f79fae87499999a74b/gates",
# #                   status=201,
# #                   json=range_gate)
# #     range_gate = experiment.create_range_gate(x_channel="FSC-A", name="my gate",
# #                                               x1=12.502,
# #                                               x2=95.102)
# #     gate_tester(range_gate)
# #     assert range_gate.model.range.x1 == 12.502
# #     assert range_gate.model.range.x2 == 95.102
# #     assert range_gate.model.range.y == 0.5


# # @responses.activate
# # def test_create_quadrant_gate(experiment, scalesets, quadrant_gate):
# #     responses.add(responses.GET,
# #                   base_url+"experiments/5d38a6f79fae87499999a74b/scalesets",
# #                   json=[scalesets])
# #     responses.add(responses.POST,
# #                   base_url+"experiments/5d38a6f79fae87499999a74b/gates",
# #                   status=201,
# #                   json=quadrant_gate)
# #     quadrant_gate = experiment.create_quadrant_gate(name='test_quadrant_gate',
# #                                                     x_channel='FSC-A',
# #                                                     y_channel='FSC-W',
# #                                                     x=160000,
# #                                                     y=200000)
# #     gate_tester(quadrant_gate)
# #     assert quadrant_gate.model.quadrant.x == 160000
# #     assert quadrant_gate.model.quadrant.y == 200000
# #     assert quadrant_gate.model.quadrant.angles == [1.5707963267948966, 3.141592653589793, 4.71238898038469, 0]
# #     assert quadrant_gate.model.gids == ['5db01cb2e4eb52e0c1047306',
# #                                         '5db01cb265909ddcfd6e2807',
# #                                         '5db01cb2486959d467563e08',
# #                                         '5db01cb21b8e42bc6499c609']
# #     assert quadrant_gate.names == ['my gate (UR)', 'my gate (UL)',
# #                                   'my gate (LL)', 'my gate (LR)']
# #     assert quadrant_gate.model.labels == [[1, 1], [-200, 1], [-200, -200], [1, -200]]


# # @responses.activate
# # def test_create_split_gate(experiment, scalesets, split_gate):
# #     responses.add(responses.GET,
# #                   base_url+"experiments/5d38a6f79fae87499999a74b/scalesets",
# #                   json=[scalesets])
# #     responses.add(responses.POST,
# #                   base_url+"experiments/5d38a6f79fae87499999a74b/gates",
# #                   status=201,
# #                   json=split_gate)
# #     split_gate = experiment.create_split_gate(x_channel="FSC-A",
# #                                               name="my gate",
# #                                               x=160000,
# #                                               y=100000)
# #     gate_tester(split_gate)
# #     assert split_gate.model.split.x == 160000
# #     assert split_gate.model.split.y == 1
# #     assert split_gate.model.gids == ['5db02aff9375ffe04e55b801', '5db02aff556563a0f01c7a02']
# #     assert split_gate.names == ['my gate (L)', 'my gate (R)']
# #     assert split_gate.model.labels == [[-199.9, 0.916], [0.9, 0.916]]
