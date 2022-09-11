import json

from cattrs.errors import ClassValidationError
import pytest
import responses

from cellengine.resources.gate import (
    EllipseGate,
    Gate,
    PolygonGate,
    QuadrantGate,
    RangeGate,
    RectangleGate,
    SplitGate,
)
from cellengine.utils.helpers import is_valid_id
from tests.unit.resources.test_population import population_tester


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
    assert hasattr(instance, "model")


def test_init_gate(ENDPOINT_BASE, client, polygon_gate):
    """Test instantiating a gate object a correct dict of properties"""
    g = Gate.from_dict(polygon_gate)
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
    g = RectangleGate.create(
        EXP_ID,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my fancy gate",
        x1=12.502,
        x2=95.102,
        y1=1020,
        y2=32021.2,
    )
    gate_tester(g)


@responses.activate
def test_create_multiple_gates_from_dicts(
    ENDPOINT_BASE, client, rectangle_gate, ellipse_gate
):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=[rectangle_gate, ellipse_gate],
    )
    g1 = {
        "experiment_id": EXP_ID,
        "type": "RectangleGate",
        "x_channel": "FSC-A",
        "y_channel": "FSC-W",
        "name": "my fancy gate",
        "x1": 12.502,
        "x2": 95.102,
        "y1": 1020,
        "y2": 32021.2,
    }
    g2 = {
        "experiment_id": EXP_ID,
        "type": "EllipseGate",
        "x_channel": "FSC-A",
        "y_channel": "FSC-W",
        "name": "my gate",
        "x": 260000,
        "y": 64000,
        "angle": 0,
        "major": 120000,
        "minor": 70000,
    }

    gates = Gate.create_many([g1, g2])
    [gate_tester(gate) for gate in gates]


def test_throws_error_for_missing_keys_in_gate_dict():
    input = {"x_channel": "FSC-A"}
    with pytest.raises(ValueError):
        RectangleGate._format(**input)


test_params = [
    (
        # only required keys
        {  # input
            "experiment_id": EXP_ID,
            "type": "RectangleGate",
            "x_channel": "FSC-A",
            "y_channel": "FSC-W",
            "name": "my fancy gate",
            "model": {
                "rectangle": {
                    "x1": 12.502,
                    "x2": 95.102,
                    "y1": 1020,
                    "y2": 32021.2,
                }
            },
        },
        {  # expected
            "experiment_id": EXP_ID,
            "type": "RectangleGate",
            "x_channel": "FSC-A",
            "y_channel": "FSC-W",
            "name": "my fancy gate",
            "tailored_per_file": False,
            "gid": None,
            "fcs_file_id": None,
            "parent_population_id": None,
            "model": {
                "rectangle": {
                    "x1": 12.502,
                    "x2": 95.102,
                    "y1": 1020,
                    "y2": 32021.2,
                },
                "label": [53.802, 16520.6],
                "locked": False,
            },
        },
    ),
    (
        # accepts other keys
        {  # input
            "experiment_id": EXP_ID,
            "type": "RectangleGate",
            "x_channel": "FSC-A",
            "y_channel": "FSC-W",
            "name": "my fancy gate",
            "gid": "my-nice-gid",
            "tailored_per_file": True,
            "fcs_file_id": "some-file-id",
            "parent_population_id": "some-parent-id",
            "model": {
                "rectangle": {
                    "x1": 12.502,
                    "x2": 95.102,
                    "y1": 1020,
                    "y2": 32021.2,
                },
                "label": [1, 1],  # label
                "locked": True,
            },
        },
        {  # expected
            "experiment_id": EXP_ID,
            "type": "RectangleGate",
            "x_channel": "FSC-A",
            "y_channel": "FSC-W",
            "name": "my fancy gate",
            "tailored_per_file": True,
            "gid": "my-nice-gid",
            "fcs_file_id": "some-file-id",
            "parent_population_id": "some-parent-id",
            "model": {
                "rectangle": {
                    "x1": 12.502,
                    "x2": 95.102,
                    "y1": 1020,
                    "y2": 32021.2,
                },
                "label": [1, 1],
                "locked": True,
            },
        },
    ),
]


def test_formats_gate_dicts_correctly(bulk_gate_creation_dict):
    for gate in bulk_gate_creation_dict:
        if gate["type"] == "QuadrantGate":
            gate["model"]["labels"] = [[1, 2], [3, 4], [5, 6], [7, 8]]

        if gate["type"] == "SplitGate":
            gate["model"]["labels"] = [[1, 2], [3, 4]]

        formatted = Gate._format_gate(gate)

        gate_model = gate.pop("model")
        formatted_model = formatted.pop("model")
        assert all([gate[key] == formatted[key] for key in formatted.keys()])
        assert all(
            [gate_model[key] == formatted_model[key] for key in formatted_model.keys()]
        )


gate_dicts = [
    (
        # only required keys
        [
            {  # input
                "experiment_id": EXP_ID,
                "type": "RectangleGate",
                "x_channel": "FSC-A",
                "y_channel": "FSC-W",
                "name": "my fancy gate",
                "model": {
                    "rectangle": {
                        "x1": 12.502,
                        "x2": 95.102,
                        "y1": 1020,
                        "y2": 32021.2,
                    }
                },
            },
            {
                "experiment_id": EXP_ID,
                "type": "EllipseGate",
                "x_channel": "FSC-A",
                "y_channel": "FSC-W",
                "name": "my gate",
                "model": {
                    "ellipse": {
                        "center": [260000, 64000],
                        "angle": 0,
                        "major": 120000,
                        "minor": 70000,
                    }
                },
            },
        ],
        [
            {  # mock response
                "_id": "returned-from-API",
                "experimentId": EXP_ID,
                "type": "RectangleGate",
                "xChannel": "FSC-A",
                "yChannel": "FSC-W",
                "name": "my fancy gate",
                "tailoredPerFile": False,
                "gid": None,
                "fcsFileId": None,
                "model": {
                    "rectangle": {
                        "x1": 12.502,
                        "x2": 95.102,
                        "y1": 1020,
                        "y2": 32021.2,
                    },
                    "label": [53.802, 16520.6],
                    "locked": False,
                },
            },
            {
                "_id": "returned-from-API",
                "experimentId": EXP_ID,
                "type": "EllipseGate",
                "xChannel": "FSC-A",
                "yChannel": "FSC-W",
                "name": "my fancy gate",
                "tailored_per_file": False,
                "gid": None,
                "fcsFileId": None,
                "model": {
                    "ellipse": {
                        "center": [260000, 64000],
                        "angle": 0,
                        "major": 120000,
                        "minor": 70000,
                    },
                    "label": [53.802, 16520.6],
                    "locked": False,
                },
            },
        ],
    ),
]


@responses.activate
@pytest.mark.parametrize("input, response", gate_dicts)
def test_creates_multiple_gates_from_dicts(client, ENDPOINT_BASE, input, response):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=response,
    )

    gates = Gate.create_many(input)
    assert isinstance(gates[0], RectangleGate)
    assert isinstance(gates[1], EllipseGate)
    [gate_tester(gate) for gate in gates]


@pytest.fixture
def bad_gate():
    bad_gate = {
        "experimentId": "5d38a6f79fae87499999a74b",
        "name": "my gate",
        # "type": "PolygonGate",
        # "gid": "5dc6e4514855ff5d3d041d03",
        # "xChannel": "FSC-A",
        # "yChannel": "FSC-W",
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


def test_create_gate_with_bad_params(client, bad_gate):
    with pytest.raises(ClassValidationError):
        g = Gate.from_dict(bad_gate)
        g.update()


@responses.activate
def test_update_gate(ENDPOINT_BASE, client, experiment, rectangle_gate):
    """Test that the .update() method makes the correct call. Does not test
    that the correct response is made; this should be done with an integration
    test.
    """
    gate = Gate.from_dict(rectangle_gate)
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
    assert json.loads(responses.calls[0].request.body)["name"] == "newname"  # type: ignore


@responses.activate
def test_update_gate_family(client, ENDPOINT_BASE, experiment, rectangle_gate):
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
    g = RectangleGate.create(
        EXP_ID,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my fancy gate",
        x1=12.502,
        x2=95.102,
        y1=1020,
        y2=32021.2,
        create_population=False,
    )
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
            responses.DELETE,
            f"{ENDPOINT_BASE}" + url,
        )
        client.delete_gate(experiment._id, **args)


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
    rectangle_gate = RectangleGate.create(
        experiment_id=EXP_ID,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        x1=60000,
        x2=200000,
        y1=75000,
        y2=215000,
        create_population=False,
    )
    gate_tester(rectangle_gate)
    m = rectangle_gate.model["rectangle"]
    assert m["x1"] == 60000
    assert m["x2"] == 200000
    assert m["y1"] == 75000
    assert m["y2"] == 215000


@responses.activate
def test_create_rectangle_gate_without_create_population(
    ENDPOINT_BASE, client, experiment, rectangle_gate
):
    """Regression test for #118."""
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
        create_population=False,
    )
    assert "createPopulation=false" in responses.calls[0].request.url  # type: ignore


@responses.activate
def test_create_rectangle_gate_creates_gate_and_population(
    ENDPOINT_BASE, client, rectangle_gate, populations
):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json={"population": populations[0], "gate": rectangle_gate},
    )
    gate, population = RectangleGate.create(
        EXP_ID,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        x1=60000,
        x2=200000,
        y1=75000,
        y2=215000,
    )
    gate_tester(gate)
    population_tester(population)


@responses.activate
def test_create_ellipse_gate(ENDPOINT_BASE, client, experiment, ellipse_gate):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=ellipse_gate,
    )
    ellipse_gate = EllipseGate.create(
        experiment_id=EXP_ID,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        center=[259441.51377370575, 63059.462213950595],
        angle=-0.16875182756633697,
        major=113446.7481834943,
        minor=70116.01916918601,
        create_population=False,
    )
    gate_tester(ellipse_gate)
    m = ellipse_gate.model["ellipse"]
    assert m["center"] == [259441.51377370575, 63059.462213950595]
    assert m["major"] == 113446.7481834943
    assert m["minor"] == 70116.01916918601
    assert m["angle"] == -0.16875182756633697


@responses.activate
def test_create_polygon_gate(ENDPOINT_BASE, client, experiment, polygon_gate):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=polygon_gate,
    )
    polygon_gate = PolygonGate.create(
        experiment_id=EXP_ID,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        vertices=[[1, 4], [2, 5], [3, 6]],
        create_population=False,
    )
    gate_tester(polygon_gate)
    assert polygon_gate.model["polygon"]["vertices"] == [
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
def test_create_range_gate(ENDPOINT_BASE, client, range_gate):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/gates",
        status=201,
        json=range_gate,
    )
    range_gate = RangeGate.create(
        experiment_id=EXP_ID,
        x_channel="FSC-A",
        name="my gate",
        x1=12.502,
        x2=95.102,
        create_population=False,
    )
    gate_tester(range_gate)
    m = range_gate.model["range"]
    assert m["x1"] == 12.502
    assert m["x2"] == 95.102
    assert m["y"] == 0.5


@responses.activate
def test_create_quadrant_gate(
    ENDPOINT_BASE, client, experiment, scalesets, quadrant_gate
):
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
    quadrant_gate = QuadrantGate.create(
        experiment_id=EXP_ID,
        name="test_quadrant_gate",
        x_channel="FSC-A",
        y_channel="FSC-W",
        x=160000,
        y=200000,
        create_population=False,
    )
    gate_tester(quadrant_gate)
    m = quadrant_gate.model
    assert m["quadrant"]["x"] == 160000
    assert m["quadrant"]["y"] == 200000
    assert m["quadrant"]["angles"] == [
        1.5707963267948966,
        3.141592653589793,
        4.71238898038469,
        0,
    ]
    assert m["gids"] == [
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
    assert quadrant_gate.model["labels"] == [[1, 1], [-200, 1], [-200, -200], [1, -200]]


def test_formats_all_gate_defaults_correctly():
    qg = QuadrantGate._format(
        experiment_id=EXP_ID,
        name="test_quadrant_gate",
        x_channel="FSC-A",
        y_channel="FSC-W",
        x=160000,
        y=200000,
        labels=[[1, 1], [-200, 1], [-200, -200], [1, -200]],
    )
    assert qg["experiment_id"] == EXP_ID
    assert qg["names"] == [
        "test_quadrant_gate (UR)",
        "test_quadrant_gate (UL)",
        "test_quadrant_gate (LL)",
        "test_quadrant_gate (LR)",
    ]
    assert qg["x_channel"] == "FSC-A"
    assert qg["y_channel"] == "FSC-W"
    m = qg["model"]
    assert m["quadrant"]["x"] == 160000
    assert m["quadrant"]["y"] == 200000
    assert m["quadrant"]["angles"] == [
        0,
        1.5707963267948966,
        3.141592653589793,
        4.71238898038469,
    ]
    assert all(is_valid_id(id) for id in m["gids"])
    assert m["labels"] == [[1, 1], [-200, 1], [-200, -200], [1, -200]]


@responses.activate
def test_formats_gate_defaults_and_generates_nudged_labels(
    ENDPOINT_BASE, client, experiment, scalesets, quadrant_gate
):
    # makes a request for the scaleset
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/scalesets",
        json=[scalesets],
    )

    qg = QuadrantGate._format(
        experiment_id=EXP_ID,
        name="test_quadrant_gate",
        x_channel="FSC-A",
        y_channel="FSC-W",
        x=160000,
        y=200000,
    )
    p = qg["model"]["labels"]
    assert qg["model"]["labels"] == [
        [233217, 247680],
        [36158, 247680],
        [36158, 13560],
        [233217, 13560],
    ]


@responses.activate
def test_create_split_gate(client, ENDPOINT_BASE, experiment, scalesets, split_gate):
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
    split_gate = SplitGate.create(
        experiment_id=EXP_ID,
        x_channel="FSC-A",
        name="my gate",
        x=160000,
        y=100000,
        create_population=False,
    )
    gate_tester(split_gate)
    m = split_gate.model["split"]
    assert m["x"] == 160000
    assert m["y"] == 1
    assert split_gate.model["gids"] == [
        "5db02aff9375ffe04e55b801",
        "5db02aff556563a0f01c7a02",
    ]
    assert split_gate.names == ["my gate (L)", "my gate (R)"]
    assert split_gate.model["labels"] == [[-199.9, 0.916], [0.9, 0.916]]
