import json
import pytest
from typing import Iterator, Tuple


from cellengine.utils.api_client.APIError import APIError
from cellengine.resources.population import Population
from cellengine.resources.gate import Gate
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile


@pytest.fixture()
def ligands_experiment(
    blank_experiment: Experiment,
) -> Iterator[Tuple[Experiment, FcsFile, Gate, Population]]:
    file1 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
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

    yield blank_experiment, file1, gate, pop


# Begin tests


def test_population_get(
    ligands_experiment: Tuple[Experiment, FcsFile, Gate, Population]
):
    experiment, _, _, population = ligands_experiment
    pop = Population.get(experiment._id, population._id)
    assert type(pop) is Population


def test_population_update(
    ligands_experiment: Tuple[Experiment, FcsFile, Gate, Population]
):
    _, _, _, population = ligands_experiment
    population.name = "newname"
    population.update()
    assert population.name == "newname"


def test_population_delete(
    ligands_experiment: Tuple[Experiment, FcsFile, Gate, Population]
):
    experiment, _, _, population = ligands_experiment
    population.delete()
    with pytest.raises(APIError):
        Population.get(experiment._id, population._id)
