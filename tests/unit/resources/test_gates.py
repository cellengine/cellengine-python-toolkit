import json
import pytest
import responses

from cellengine.resources.gate import (
    Gate,
    RectangleGate,
    EllipseGate,
)
from cellengine.utils.api_client.APIError import APIError


EXP_ID = "5d38a6f79fae87499999a74b"


def gate_tester(instance):
    """Generalize tests for shared gate fields"""
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


def test_init_gate(ENDPOINT_BASE, client, polygon_gate):
    """Test instantiating a gate object a correct dict of properties"""
    g = Gate.factory(polygon_gate)
    gate_tester(g)
    assert g.experiment_id == EXP_ID
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
def test_create_one_gate(ENDPOINT_BASE, client, rectangle_gate):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=rectangle_gate,
    )
    g = Gate.factory(rectangle_gate)
    g.post()
    gate_tester(g)


@responses.activate
def test_create_multiple_gates_from_dicts(
    ENDPOINT_BASE, client, rectangle_gate, polygon_gate
):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=[rectangle_gate, rectangle_gate, polygon_gate],
    )
    new_gates = [rectangle_gate, rectangle_gate, polygon_gate]
    gates = Gate.bulk_create(EXP_ID, new_gates)
    [gate_tester(gate) for gate in gates]


@responses.activate
def test_create_multiple_gates_from_gate_objects(
    ENDPOINT_BASE, client, rectangle_gate, polygon_gate
):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=[rectangle_gate, rectangle_gate, polygon_gate],
    )
    g1 = RectangleGate.create(
        EXP_ID,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my fancy gate",
        x1=12.502,
        x2=95.102,
        y1=1020,
        y2=32021.2,
    )
    g2 = RectangleGate.create(
        EXP_ID,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my other gate",
        x1=12.502,
        x2=95.102,
        y1=1020,
        y2=32021.2,
    )
    g3 = EllipseGate.create(
        experiment_id=EXP_ID,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        x=260000,
        y=64000,
        angle=0,
        major=120000,
        minor=70000,
    )
    gates = Gate.bulk_create(EXP_ID, [g1, g2, g3])
    [gate_tester(gate) for gate in gates]

    # gates = Gate.factory([rectangle_gate, rectangle_gate])
    # gate_tester(gates[0])
    # gate_tester(gates[1])
    # Gate.post(gates)


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
def test_create_gate_with_bad_params(ENDPOINT_BASE, client, bad_gate):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=400,
        json={"error": '"gid" is required.'},
    )
    with pytest.raises(APIError):
        g = Gate.factory(bad_gate)
        g.post()


@responses.activate
def test_update_gate(ENDPOINT_BASE, client, experiment, rectangle_gate):
    """Test that the .update() method makes the correct call. Does not test
    that the correct response is made; this should be done with an integration
    test.
    """
    gate = Gate.factory(rectangle_gate)
    # patch the mocked response with the correct values
    response = rectangle_gate.copy()
    response.update({"name": "newname"})
    responses.add(
        responses.PATCH,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates/{rectangle_gate['_id']}",
        json=response,
    )
    gate.name = "newname"
    gate.update()

    gate_tester(gate)
    assert json.loads(responses.calls[0].request.body) == gate._properties


@responses.activate
def test_update_gate_family(ENDPOINT_BASE, experiment, rectangle_gate):
    gid = rectangle_gate["gid"]
    responses.add(
        responses.PATCH,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates?gid={gid}",
        status=201,
        json={"nModified": 1},
    )
    Gate.update_gate_family(experiment._id, gid, {"xChannel": "newChannel"})


@responses.activate
def test_should_delete_gate(ENDPOINT_BASE, client, rectangle_gate):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=rectangle_gate,
    )
    responses.add(
        responses.DELETE,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates/{rectangle_gate['_id']}",
    )
    g = Gate.factory(rectangle_gate)
    g.post()
    gate_tester(g)
    g.delete()


class TestShouldDeleteGates:
    """Delete a gate or gate family, optionally excluding a gate from deletion"""

    gate_id = "5d8d34994e84a1e661f157a1"
    gid = "5d8d34993b0bb307a31d9d04"
    delete_params = [
        ({"_id": gate_id}, f"/experiments/{EXP_ID}/gates/{gate_id}"),
        ({"gid": gid}, f"/experiments/{EXP_ID}/gates?gid={gid}"),
        (
            {"gid": gid, "exclude": gate_id},
            f"/experiments/{EXP_ID}/gates?gid={gid}%exclude={gate_id}",
        ),
    ]

    @responses.activate
    @pytest.mark.parametrize("args,url", delete_params)
    def test_should_delete_gates(
        self, ENDPOINT_BASE, client, experiment, rectangle_gate, args, url
    ):
        responses.add(
            responses.DELETE, f"{ENDPOINT_BASE}" + url,
        )
        Gate.delete_gates(experiment._id, **args)


@responses.activate
def test_create_rectangle_gate(ENDPOINT_BASE, client, experiment, rectangle_gate):
    """Test rectangle gate creation.

    Note that the returned object may not have values that match the request.
    This is because the returned object is built from a dict returned by a
    pytest fixture (intercepted by `responses`), not by the CE API.
    """
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=rectangle_gate,
    )
    rectangle_gate = experiment.create_rectangle_gate(
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        x1=60000,
        x2=200000,
        y1=75000,
        y2=215000,
    )
    rectangle_gate.post()
    gate_tester(rectangle_gate)
    assert rectangle_gate.model.rectangle.x1 == 60000
    assert rectangle_gate.model.rectangle.x2 == 200000
    assert rectangle_gate.model.rectangle.y1 == 75000
    assert rectangle_gate.model.rectangle.y2 == 215000


@responses.activate
def test_create_ellipse_gate(ENDPOINT_BASE, client, experiment, ellipse_gate):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=ellipse_gate,
    )
    ellipse_gate = experiment.create_ellipse_gate(
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        x=259441.51377370575,
        y=63059.462213950595,
        angle=-0.16875182756633697,
        major=113446.7481834943,
        minor=70116.01916918601,
    )
    ellipse_gate.post()
    gate_tester(ellipse_gate)
    assert ellipse_gate.model.ellipse.center == [259441.51377370575, 63059.462213950595]
    assert ellipse_gate.model.ellipse.major == 113446.7481834943
    assert ellipse_gate.model.ellipse.minor == 70116.01916918601
    assert ellipse_gate.model.ellipse.angle == -0.16875182756633697


@responses.activate
def test_create_polygon_gate(ENDPOINT_BASE, client, experiment, polygon_gate):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=polygon_gate,
    )
    polygon_gate = experiment.create_polygon_gate(
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        vertices=[[1, 4], [2, 5], [3, 6]],
    )
    polygon_gate.post()
    gate_tester(polygon_gate)
    assert polygon_gate.model.polygon.vertices == [
        [59456.113402061856, 184672.1855670103],
        [141432.10309278348, 181068.84536082475],
        [82877.82474226804, 124316.23711340204],
        [109002.0412371134, 63960.28865979381],
        [44141.9175257732, 76571.97938144332],
        [27926.886597938144, 107200.37113402062],
        [10811.0206185567, 143233.77319587627],
        [58555.278350515466, 145936.27835051547],
    ]


@responses.activate
def test_create_range_gate(ENDPOINT_BASE, experiment, range_gate):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=range_gate,
    )
    range_gate = experiment.create_range_gate(
        x_channel="FSC-A", name="my gate", x1=12.502, x2=95.102
    )
    range_gate.post()
    gate_tester(range_gate)
    assert range_gate.model.range.x1 == 12.502
    assert range_gate.model.range.x2 == 95.102
    assert range_gate.model.range.y == 0.5


@responses.activate
def test_create_quadrant_gate(ENDPOINT_BASE, experiment, scalesets, quadrant_gate):
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/scalesets",
        json=[scalesets],
    )
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=quadrant_gate,
    )
    quadrant_gate = experiment.create_quadrant_gate(
        name="test_quadrant_gate",
        x_channel="FSC-A",
        y_channel="FSC-W",
        x=160000,
        y=200000,
    )
    quadrant_gate.post()
    gate_tester(quadrant_gate)
    assert quadrant_gate.model.quadrant.x == 160000
    assert quadrant_gate.model.quadrant.y == 200000
    assert quadrant_gate.model.quadrant.angles == [
        1.5707963267948966,
        3.141592653589793,
        4.71238898038469,
        0,
    ]
    assert quadrant_gate.model.gids == [
        "5db01cb2e4eb52e0c1047306",
        "5db01cb265909ddcfd6e2807",
        "5db01cb2486959d467563e08",
        "5db01cb21b8e42bc6499c609",
    ]
    assert quadrant_gate.names == [
        "my gate (UR)",
        "my gate (UL)",
        "my gate (LL)",
        "my gate (LR)",
    ]
    assert quadrant_gate.model.labels == [[1, 1], [-200, 1], [-200, -200], [1, -200]]


@responses.activate
def test_create_split_gate(ENDPOINT_BASE, experiment, scalesets, split_gate):
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/scalesets",
        json=[scalesets],
    )
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=split_gate,
    )
    split_gate = experiment.create_split_gate(
        x_channel="FSC-A", name="my gate", x=160000, y=100000
    )
    split_gate.post()
    gate_tester(split_gate)
    assert split_gate.model.split.x == 160000
    assert split_gate.model.split.y == 1
    assert split_gate.model.gids == [
        "5db02aff9375ffe04e55b801",
        "5db02aff556563a0f01c7a02",
    ]
    assert split_gate.names == ["my gate (L)", "my gate (R)"]
    assert split_gate.model.labels == [[-199.9, 0.916], [0.9, 0.916]]
