import json
from typing import Iterator, Tuple, List
import pytest

from cellengine.resources.gate import (
    EllipseGate,
    Gate,
    PolygonGate,
    QuadrantGate,
    RangeGate,
    RectangleGate,
    SplitGate,
)
from cellengine.resources.population import Population
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile


@pytest.fixture()
def ligands_experiment(
    blank_experiment: Experiment,
) -> Iterator[Tuple[Experiment, List[FcsFile], Gate, Population]]:
    file1 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
    )
    file2 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A2_A02_MeOHperm(DL350neg).fcs"
    )

    gate = blank_experiment.create_rectangle_gate(
        name="test gate",
        x_channel="FSC-A",
        y_channel="SSC-A",
        x1=10,
        x2=100000,
        y1=10,
        y2=100000,
        create_population=False,
    )

    pop = blank_experiment.create_population(
        {
            "name": "Pop 1",
            "gates": json.dumps({"$and": [gate.gid]}),
            "parent_id": None,
            "terminal_gate_gid": gate.gid,
        }
    )

    yield blank_experiment, [file1, file2], gate, pop


# Begin tests


def test_rectangle_gate_create(blank_experiment):
    gate = RectangleGate.create(
        experiment_id=blank_experiment._id,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        x1=60000,
        x2=200000,
        y1=75000,
        y2=215000,
        create_population=False,
    )
    assert gate.experiment_id == blank_experiment._id
    assert gate.name == "my gate"
    assert gate.type == "RectangleGate"
    assert hasattr(gate, "gid")
    assert gate.x_channel == "FSC-A"
    assert gate.y_channel == "FSC-W"
    assert gate.tailored_per_file == False
    assert gate.fcs_file_id == None
    assert hasattr(gate, "model")
    m = gate.model["rectangle"]
    assert m["x1"] == 60000
    assert m["x2"] == 200000
    assert m["y1"] == 75000
    assert m["y2"] == 215000


def test_rectangle_gate_create_with_create_population(blank_experiment):
    gate, population = RectangleGate.create(
        experiment_id=blank_experiment._id,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        x1=60000,
        x2=200000,
        y1=75000,
        y2=215000,
        create_population=True,
    )
    assert isinstance(gate, RectangleGate)
    assert gate.name == "my gate"
    assert isinstance(population, Population)
    assert population.name == "my gate"
    assert population.terminal_gate_gid == gate.gid
    assert population.parent_id == None


def test_ellipse_gate_create(blank_experiment):
    gate = EllipseGate.create(
        experiment_id=blank_experiment._id,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        center=[259441.51377370575, 63059.462213950595],
        angle=-0.16875182756633697,
        major=113446.7481834943,
        minor=70116.01916918601,
        create_population=False,
    )
    assert gate.experiment_id == blank_experiment._id
    assert gate.name == "my gate"
    assert gate.type == "EllipseGate"
    assert hasattr(gate, "gid")
    assert gate.x_channel == "FSC-A"
    assert gate.y_channel == "FSC-W"
    assert gate.tailored_per_file == False
    assert gate.fcs_file_id == None
    assert hasattr(gate, "model")
    m = gate.model["ellipse"]
    assert m["center"] == [259441.51377370575, 63059.462213950595]
    assert m["major"] == 113446.7481834943
    assert m["minor"] == 70116.01916918601
    assert m["angle"] == -0.16875182756633697


def test_polygon_gate_create(blank_experiment):
    gate = PolygonGate.create(
        experiment_id=blank_experiment._id,
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="my gate",
        vertices=[[1, 4], [2, 5], [3, 6]],
        create_population=False,
    )
    assert gate.experiment_id == blank_experiment._id
    assert gate.name == "my gate"
    assert gate.type == "PolygonGate"
    assert hasattr(gate, "gid")
    assert gate.x_channel == "FSC-A"
    assert gate.y_channel == "FSC-W"
    assert gate.tailored_per_file == False
    assert gate.fcs_file_id == None
    assert hasattr(gate, "model")
    assert gate.model["polygon"]["vertices"] == [[1, 4], [2, 5], [3, 6]]


def test_range_gate_create(blank_experiment):
    gate = RangeGate.create(
        experiment_id=blank_experiment._id,
        x_channel="FSC-A",
        name="my gate",
        x1=12.502,
        x2=95.102,
        create_population=False,
    )
    assert gate.experiment_id == blank_experiment._id
    assert gate.name == "my gate"
    assert gate.type == "RangeGate"
    assert hasattr(gate, "gid")
    assert gate.x_channel == "FSC-A"
    assert gate.tailored_per_file == False
    assert gate.fcs_file_id == None
    assert hasattr(gate, "model")
    m = gate.model["range"]
    assert m["x1"] == 12.502
    assert m["x2"] == 95.102
    assert m["y"] == 0.5


def test_quadrant_gate_create(ligands_experiment):
    experiment, _, _, _ = ligands_experiment
    gate = QuadrantGate.create(
        experiment_id=experiment._id,
        name="my gate",
        x_channel="FSC-A",
        y_channel="FSC-W",
        x=160000,
        y=200000,
        create_population=False,
    )
    assert gate.experiment_id == experiment._id
    assert gate.type == "QuadrantGate"
    assert hasattr(gate, "gid")
    assert gate.x_channel == "FSC-A"
    assert gate.y_channel == "FSC-W"
    assert gate.tailored_per_file == False
    assert gate.fcs_file_id == None
    assert hasattr(gate, "model")
    m = gate.model
    assert m["quadrant"]["x"] == 160000
    assert m["quadrant"]["y"] == 200000
    assert m["quadrant"]["angles"] == [
        0,
        1.5707963267948966,
        3.141592653589793,
        4.71238898038469,
    ]
    assert isinstance(gate.model["gids"], list) and len(gate.model["gids"]) == 4
    assert gate.names == [
        "my gate (UR)",
        "my gate (UL)",
        "my gate (LL)",
        "my gate (LR)",
    ]
    assert gate.model["labels"] == [
        [1e38, 1e38],
        [-1e38, 1e38],
        [-1e38, -1e38],
        [1e38, -1e38],
    ]


def test_split_gate_create(ligands_experiment):
    experiment, _, _, _ = ligands_experiment
    gate = SplitGate.create(
        experiment_id=experiment._id,
        x_channel="FSC-A",
        name="my gate",
        x=160000,
        y=1,
        create_population=False,
    )
    assert gate.experiment_id == experiment._id
    assert gate.type == "SplitGate"
    assert hasattr(gate, "gid")
    assert gate.x_channel == "FSC-A"
    assert gate.tailored_per_file == False
    assert gate.fcs_file_id == None
    assert hasattr(gate, "model")
    m = gate.model["split"]
    assert m["x"] == 160000
    assert m["y"] == 1
    assert isinstance(gate.model["gids"], list) and len(gate.model["gids"]) == 2
    assert gate.names == ["my gate (L)", "my gate (R)"]
    assert gate.model["labels"] == [[-1e38, 1], [1e38, 1]]


def test_gate_create_many(blank_experiment):
    g1 = {
        "experiment_id": blank_experiment._id,
        "type": "RectangleGate",
        "x_channel": "FSC-A",
        "y_channel": "FSC-W",
        "name": "my gate 1",
        "x1": 12.502,
        "x2": 95.102,
        "y1": 1020,
        "y2": 32021.2,
    }
    g2 = {
        "experiment_id": blank_experiment._id,
        "type": "EllipseGate",
        "x_channel": "FSC-A",
        "y_channel": "FSC-W",
        "name": "my gate 2",
        "x": 260000,
        "y": 64000,
        "angle": 0,
        "major": 120000,
        "minor": 70000,
    }

    gates = Gate.create_many([g1, g2])
    [isinstance(gate, Gate) for gate in gates]


def test_gate_delete(ligands_experiment):
    experiment, _, gate, _ = ligands_experiment
    gate.delete()
    assert experiment.gates == []


def test_gate_update(ligands_experiment):
    experiment, _, gate, _ = ligands_experiment
    gate.name = "newname"
    gate.update()
    g = experiment.get_gate(gate._id)
    assert g.name == "newname"


def test_gate_update_gate_family(ligands_experiment):
    experiment, _, gate, _ = ligands_experiment
    gid = gate.gid
    Gate.update_gate_family(experiment._id, gid, {"name": "new name"})
    g = experiment.get_gate(gate._id)
    assert g.name == "new name"


def test_gate_apply_tailoring(ligands_experiment):
    experiment, fcs_files, gate, _ = ligands_experiment

    # Global
    global_gate, pop = experiment.create_rectangle_gate(
        x_channel=fcs_files[0].channels[0],
        y_channel=fcs_files[0].channels[1],
        name="gate 1",
        x1=10,
        y1=10,
        x2=20,
        y2=20,
        create_population=True,
        tailored_per_file=True,
        fcs_file_id=None,
    )

    # Tailored to f0
    f0_gate = experiment.create_rectangle_gate(
        x_channel=fcs_files[0].channels[0],
        y_channel=fcs_files[0].channels[1],
        name="gate 1",
        x1=50,
        y1=50,
        x2=70,
        y2=70,
        tailored_per_file=True,
        fcs_file_id=fcs_files[0]._id,
        gid=global_gate.gid,
        create_population=False,
    )

    # Apply to f1 should insert a gate for that file
    res1 = f0_gate.apply_tailoring([fcs_files[1]._id])
    print(res1)
    assert len(res1.inserted) == 1
    assert len(res1.updated) == 0
    assert len(res1.deleted) == 0
    assert res1.inserted[0].fcs_file_id == fcs_files[1]._id

    # Apply global to f1 should delete f1's tailored gate
    res2 = global_gate.apply_tailoring([fcs_files[1]._id])
    assert len(res2.inserted) == 0
    assert len(res2.updated) == 0
    assert len(res2.deleted) == 1
    assert res2.deleted[0] == res1.inserted[0]._id
