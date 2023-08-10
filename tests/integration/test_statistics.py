import json
from typing import Iterator, Tuple, List
import pytest
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from cellengine.resources.gate import Gate
from cellengine.resources.population import Population
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.compensation import FILE_INTERNAL


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


def test_experiment_get_statistics(ligands_experiment):
    experiment, files, _, pop = ligands_experiment
    stats = experiment.get_statistics(
        statistics=["eventCount", "mean", "median", "percent", "quantile"],
        channels=["FSC-A", "SSC-A"],
        q=0.9,
        compensation_id=FILE_INTERNAL,
        percent_of="PARENT",
        population_ids=[pop._id],
    )
    print(stats.to_string())
    assert_frame_equal(
        stats,
        DataFrame(
            [
                [
                    files[0]._id,
                    "Specimen_001_A1_A01_MeOHperm(DL350neg).fcs",
                    pop._id,
                    "Pop 1",
                    "Pop 1",
                    "Ungated",
                    None,
                    {
                        "plate": "96 Well - V bottom",
                        "plate row": "A",
                        "plate column": "01",
                        "plate well": "A01",
                    },
                    None,
                    "Ungated",
                    "Ungated",
                    88.828197,
                    158068,
                    "FSC-A",
                    "FSC-A",
                    51334.479327,
                    49697.291016,
                    69713.179688,
                ],
                [
                    files[0]._id,
                    "Specimen_001_A1_A01_MeOHperm(DL350neg).fcs",
                    pop._id,
                    "Pop 1",
                    "Pop 1",
                    "Ungated",
                    None,
                    {
                        "plate": "96 Well - V bottom",
                        "plate row": "A",
                        "plate column": "01",
                        "plate well": "A01",
                    },
                    None,
                    "Ungated",
                    "Ungated",
                    88.828197,
                    158068,
                    "SSC-A",
                    "SSC-A",
                    45705.917591,
                    34502.160156,
                    87184.095052,
                ],
                [
                    files[1]._id,
                    "Specimen_001_A2_A02_MeOHperm(DL350neg).fcs",
                    pop._id,
                    "Pop 1",
                    "Pop 1",
                    "Ungated",
                    None,
                    {
                        "plate": "96 Well - V bottom",
                        "plate row": "A",
                        "plate column": "02",
                        "plate well": "A02",
                    },
                    None,
                    "Ungated",
                    "Ungated",
                    88.056520,
                    145015,
                    "FSC-A",
                    "FSC-A",
                    51419.930670,
                    49723.562500,
                    69735.382812,
                ],
                [
                    files[1]._id,
                    "Specimen_001_A2_A02_MeOHperm(DL350neg).fcs",
                    pop._id,
                    "Pop 1",
                    "Pop 1",
                    "Ungated",
                    None,
                    {
                        "plate": "96 Well - V bottom",
                        "plate row": "A",
                        "plate column": "02",
                        "plate well": "A02",
                    },
                    None,
                    "Ungated",
                    "Ungated",
                    88.056520,
                    145015,
                    "SSC-A",
                    "SSC-A",
                    45881.525663,
                    34792.558594,
                    87595.203125,
                ],
            ],
            columns=[
                "fcsFileId",
                "filename",
                "populationId",
                "population",
                "uniquePopulationName",
                "parentPopulation",
                "parentPopulationId",
                "annotations",
                "percentOfId",
                "percentOf",
                "percentOfUniqueName",
                "percent",
                "eventCount",
                "channel",
                "reagent",
                "mean",
                "median",
                "quantile",
            ],
        ),
    )
