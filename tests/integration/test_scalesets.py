import pytest
from pandas.testing import assert_series_equal
from pandas import Series
from typing import Iterator, Tuple

from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.scaleset import ScaleSet


@pytest.fixture()
def ligands_experiment(
    blank_experiment: Experiment,
) -> Iterator[Tuple[Experiment, FcsFile]]:
    file1 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
    )

    yield blank_experiment, file1


# Begin tests


def test_scale_set_get(ligands_experiment: Tuple[Experiment, FcsFile]):
    experiment, _ = ligands_experiment
    s = ScaleSet.get(experiment._id)
    assert isinstance(s, ScaleSet)


def test_scale_set_scales_property(ligands_experiment: Tuple[Experiment, FcsFile]):
    experiment, _ = ligands_experiment
    s = ScaleSet.get(experiment._id)
    assert s.scales["FSC-A"]["type"] == "LinearScale"
    assert s.scales["FSC-A"]["minimum"] == 1
    assert s.scales["FSC-A"]["maximum"] == 262144


def test_scale_set_update(ligands_experiment: Tuple[Experiment, FcsFile]):
    pass
    experiment, _ = ligands_experiment
    s = ScaleSet.get(experiment._id)

    s.scales["FSC-A"]["maximum"] = 10
    s.update()
    assert s.scales["FSC-A"]["maximum"] == 10


def test_scale_set_apply(ligands_experiment: Tuple[Experiment, FcsFile]):
    experiment, file = ligands_experiment

    scaleset = ScaleSet(
        {
            "_id": "SCALESET_ID",
            "experimentId": experiment._id,
            "name": "Scale Set 2",
            "scales": [
                {
                    "channelName": "Time",
                    "scale": {"type": "LinearScale", "minimum": 1500, "maximum": 10000},
                },
                {
                    "channelName": "Red670-A",
                    "scale": {
                        "type": "ArcSinhScale",
                        "minimum": -200,
                        "maximum": 500,
                        "cofactor": 5,
                    },
                },
                {
                    "channelName": "SSC-W",
                    "scale": {"type": "LogScale", "minimum": 1, "maximum": 80000},
                },
            ],
        }
    )

    data = file.get_events(preSubsampleN=10, seed=1, inplace=True)
    assert_series_equal(
        data["Time"]["Time"],
        Series(
            [
                1108.4,
                1595.3,
                5737.7,
                5834.0,
                5988.7,
                7777.9,
                8819.5,
                9726.3,
                10923.5,
                13928.2,
            ],
            dtype="float32",
            name="Time",
        ),
    )
    assert_series_equal(
        data["Red670-A"]["Red670-A"],
        Series(
            [
                190.40001,
                168.3,
                96.9,
                275.4,
                670.65,
                188.70001,
                157.25,
                371.45,
                21.25,
                138.55,
            ],
            dtype="float32",
            name="Red670-A",
        ),
    )
    assert_series_equal(
        data["SSC-W"]["SSC-W"],
        Series(
            [
                72856.445,
                72080.41,
                72336.734,
                67733.805,
                82389.39,
                71159.43,
                72096.49,
                88709.07,
                69124.34,
                70477.14,
            ],
            dtype="float32",
            name="SSC-W",
        ),
    )

    output = scaleset.apply(file, clamp_q=True, in_place=False)
    assert_series_equal(
        output["Time"]["Time"],
        Series(
            [
                1500,
                1595.3,
                5737.7,
                5834.0,
                5988.7,
                7777.9,
                8819.5,
                9726.3,
                10000,
                10000,
            ],
            dtype="float32",
            name="Time",
        ),
    )
    assert_series_equal(
        output["Red670-A"]["Red670-A"],
        Series(
            [
                4.333009,
                4.209678,
                3.6580536,
                4.7020164,
                5.298342,
                4.3240433,
                4.141799,
                5.0011687,
                2.153628,
                4.015266,
            ],
            dtype="float32",
            name="Red670-A",
        ),
    )
    assert_series_equal(
        output["SSC-W"]["SSC-W"],
        Series(
            [
                4.862468,
                4.857817,
                4.859359,
                4.8308053,
                4.90309,
                4.8522325,
                4.857914,
                4.90309,
                4.839631,
                4.848048,
            ],
            dtype="float32",
            name="SSC-W",
        ),
    )
