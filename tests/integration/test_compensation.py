import pytest
from typing import Iterator, Tuple
from pandas import DataFrame
from pandas.testing import assert_frame_equal

import pandas as pd

from cellengine.utils.api_client.APIClient import APIClient
from cellengine.utils.api_client.APIError import APIError
from cellengine.resources.compensation import Compensation
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile


@pytest.fixture()
def experiment_with_compensation(
    run_id: str, client: APIClient
) -> Iterator[Tuple[Experiment, Compensation]]:
    exp_name = f"Ligands {run_id}"
    print(f"Setting up CellEngine experiment {exp_name}")
    exp = Experiment.create(exp_name)
    comp = exp.create_compensation(
        name="test_comp", channels=["a", "b"], spill_matrix=[1, 0, 0, 1]
    )

    yield exp, comp

    print(f"Starting teardown of {exp_name}")
    client.delete_experiment(exp._id)


@pytest.fixture()
def ligands_experiment(
    blank_experiment: Experiment,
) -> Iterator[Tuple[Experiment, FcsFile]]:
    file1 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
    )

    yield blank_experiment, file1


# Begin tests


def test_compensation_get_compensation_by_name(
    experiment_with_compensation: Tuple[Experiment, Compensation]
):
    experiment, compensation = experiment_with_compensation
    att = Compensation.get(experiment._id, name=compensation.name)
    assert type(att) is Compensation


def test_compensation_get_compensation_by_id(
    experiment_with_compensation: Tuple[Experiment, Compensation]
):
    experiment, compensation = experiment_with_compensation
    att = Compensation.get(experiment._id, compensation._id)
    assert type(att) is Compensation


def test_create_compensation_from_channels_and_spill_matrix(
    blank_experiment: Experiment,
):
    comp = blank_experiment.create_compensation(
        name="test_comp", channels=["a", "b"], spill_matrix=[1, 0, 0, 1]
    )
    assert type(comp) is Compensation
    assert hasattr(comp, "_id")
    assert comp.name == "test_comp"
    assert comp.experiment_id == blank_experiment._id
    assert comp.channels == ["a", "b"]
    assert comp.N == 2
    assert hasattr(comp, "dataframe")
    assert type(comp.dataframe) is DataFrame
    assert all(comp.dataframe.index == comp.channels)


def test_create_compensation_from_dataframe(blank_experiment: Experiment):
    df = DataFrame([[1, 0], [0, 1]], columns=["a", "b"], index=["a", "b"])
    comp = blank_experiment.create_compensation(name="test_comp", dataframe=df)
    assert type(comp) is Compensation
    assert hasattr(comp, "_id")
    assert comp.name == "test_comp"
    assert comp.experiment_id == blank_experiment._id
    assert comp.channels == ["a", "b"]
    assert comp.N == 2
    assert hasattr(comp, "dataframe")
    assert type(comp.dataframe) is DataFrame
    assert all(comp.dataframe.index == comp.channels)


def test_create_compensation_raises_TypeError_for_bad_args(
    blank_experiment: Experiment,
):
    expt_id = blank_experiment._id
    with pytest.raises(TypeError) as err:
        Compensation.create(expt_id, "test-comp", spill_matrix=[0, 1])  # type: ignore
    assert err.value.args[0] == "Both 'channels' and 'spill_matrix' are required."

    with pytest.raises(TypeError) as err:
        Compensation.create(expt_id, "test-comp", channels=["a", "b"])  # type: ignore
    assert err.value.args[0] == "Both 'channels' and 'spill_matrix' are required."

    with pytest.raises(TypeError) as err:
        Compensation.create(  # type: ignore
            expt_id, "test-comp", channels=["a", "b"], dataframe=DataFrame()
        )
    assert err.value.args[0] == (
        "Only one of 'dataframe' or {'channels', 'spill_matrix'} may be assigned."
    )


def test_should_delete_compensation(
    experiment_with_compensation: Tuple[Experiment, Compensation]
):
    experiment, compensation = experiment_with_compensation
    compensation.delete()
    with pytest.raises(APIError):
        Compensation.get(experiment._id, compensation._id)


def test_should_update_compensation(
    experiment_with_compensation: Tuple[Experiment, Compensation]
):
    _, compensation = experiment_with_compensation
    compensation.name = "newname"
    compensation.update()
    assert compensation.name == "newname"


def test_create_from_spill_string():
    spillstring = (
        """
    '14,Ax488-A,PE-A,PE-TR-A,PerCP-Cy55-A,PE-Cy7-A,Ax647-A,Ax700-A,Ax750-A,PacBlu-A,Qdot525-
    A,PacOrange-A,Qdot605-A,Qdot655-A,Qdot705-A,1,0.13275251154306414,0.022299626990118084,0
    .004878042437009129,0,0.023414331795661554,0,0.0001045193688180274,0,0.00232054090471367
    06,0,0.0015794832917931567,0,0,0.014120514856008378,1,0.20396581209146827,0.068600613252
    66388,0.005574843072910521,0.006309243886188101,0.0006609691554180386,0.0003004405167904
    172,0.00008003496282569645,0.0017626160950411506,0.10476698396462747,0.05058088553554031
    ,0.014527973484650415,0.0037922424631924175,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0.00179663486166
    19662,0.007212804344713549,0,1,0.16321009952978738,0.21992770547111068,0.399278611141278
    7,0.2678088269888597,0.004329151406987344,0.010822922018408362,0.004328296174818103,0.00
    28867642317136444,0.02669072659509929,0.5006316964230421,0.0035277830203874565,0.0423411
    3386077418,0.009547515616566844,0.00664175690713028,1,0.021108333327899742,0.00728518086
    0798545,0.3453922687555398,0.0009963316107540721,0.0011625273878571583,0.003985057917970
    354,0.004317271735840328,0.0008302206021389921,0.0021586181363940048,0,0.000063403793860
    01867,0.0000836951385606204,0.0009786546586352228,0.0002700164311001327,1,0.130528569869
    7553,0.07888821940265825,0,0,0.00027040048369592155,0,0.000877588608529122,0.00048823727
    034341354,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0.0061797770573503415,
    0.0007270153315273468,0.0010907250874644793,0.00036357794934124843,0.0003635835242425773
    6,0.03697642209421769,0.003272251371442924,0.0013089003597669736,1,0.3301341962836818,0.
    08900525339199582,0.027341699433188493,0.009307740439747515,0.0026178829729397984,0,0,0,
    0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1'
    """.replace(
            "\n", ""
        )
        .replace("'", "")
        .replace(" ", "")
    )

    comp = Compensation.from_spill_string(spillstring)
    assert type(comp) is Compensation

    assert comp.channels == [
        "Ax488-A",
        "PE-A",
        "PE-TR-A",
        "PerCP-Cy55-A",
        "PE-Cy7-A",
        "Ax647-A",
        "Ax700-A",
        "Ax750-A",
        "PacBlu-A",
        "Qdot525-A",
        "PacOrange-A",
        "Qdot605-A",
        "Qdot655-A",
        "Qdot705-A",
    ]


def test_apply_comp_raises_for_no_matching_channels(
    ligands_experiment: Tuple[Experiment, FcsFile]
):
    experiment, fcs_file = ligands_experiment
    comp = experiment.create_compensation(
        name="test_comp", channels=["a", "b"], spill_matrix=[1, 0, 0, 1]
    )
    with pytest.raises(KeyError):
        comp.apply(fcs_file)


def test_apply_compensation_to_fcs_file(ligands_experiment: Tuple[Experiment, FcsFile]):
    _, fcs_file = ligands_experiment

    events = fcs_file.get_events(inplace=True)

    # Pre-check uncompensated events (first event)
    assert_frame_equal(
        events.head(1),
        pd.DataFrame(
            [
                [
                    29799.06055,
                    29806,
                    65520.73828,
                    37495.03906,
                    37294,
                    65889.28906,
                    3307.040039,
                    1084.680054,
                    26838.24023,
                    209.25,
                    89.25,
                    116.8200073,
                    326.7000122,
                    153.1200104,
                    0,
                ]
            ],
            columns=[
                [
                    "FSC-A",
                    "FSC-H",
                    "FSC-W",
                    "SSC-A",
                    "SSC-H",
                    "SSC-W",
                    "Blue530-A",
                    "Vio450-A",
                    "Vio605-A",
                    "UV450-A",
                    "Red670-A",
                    "YG582-A",
                    "YG610-A",
                    "YG780-A",
                    "Time",
                ],
                [
                    "FSC-A",
                    "FSC-H",
                    "FSC-W",
                    "SSC-A",
                    "SSC-H",
                    "SSC-W",
                    "Blue530-A",
                    "Vio450-A",
                    "Vio605-A",
                    "UV450-A",
                    "Red670-A",
                    "YG582-A",
                    "YG610-A",
                    "YG780-A",
                    "Time",
                ],
            ],
            dtype="float32",
        ),
    )

    comp = fcs_file.get_file_internal_compensation()
    comp.apply(fcs_file, inplace=True)

    assert_frame_equal(
        fcs_file.events.head(1),
        pd.DataFrame(
            [
                [
                    29799.06055,
                    29806,
                    65520.73828,
                    37495.03906,
                    37294,
                    65889.28906,
                    3226.56958,
                    735.9743042,
                    26823.52148,
                    168.7714081,
                    89.25,
                    116.8200073,
                    326.7000122,
                    153.1200104,
                    0,
                ]
            ],
            columns=[
                [
                    "FSC-A",
                    "FSC-H",
                    "FSC-W",
                    "SSC-A",
                    "SSC-H",
                    "SSC-W",
                    "Blue530-A",
                    "Vio450-A",
                    "Vio605-A",
                    "UV450-A",
                    "Red670-A",
                    "YG582-A",
                    "YG610-A",
                    "YG780-A",
                    "Time",
                ],
                [
                    "FSC-A",
                    "FSC-H",
                    "FSC-W",
                    "SSC-A",
                    "SSC-H",
                    "SSC-W",
                    "Blue530-A",
                    "Vio450-A",
                    "Vio605-A",
                    "UV450-A",
                    "Red670-A",
                    "YG582-A",
                    "YG610-A",
                    "YG780-A",
                    "Time",
                ],
            ],
            dtype="float32",
        ),
    )
