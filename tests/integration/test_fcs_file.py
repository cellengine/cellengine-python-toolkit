import pandas
import os
from typing import Iterator, Tuple, List
from pandas.core.frame import DataFrame
import pytest

import cellengine
from cellengine.utils.api_client.APIError import APIError
from cellengine.resources.compensation import Compensation
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile


@pytest.fixture()
def ligands_experiment(
    blank_experiment: Experiment,
) -> Iterator[Tuple[Experiment, List[FcsFile]]]:
    file1 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
    )
    file2 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A2_A02_MeOHperm(DL350neg).fcs"
    )

    yield blank_experiment, [file1, file2]


# Begin tests


def test_fcs_file_get_by_id(ligands_experiment):
    experiment, files = ligands_experiment
    fcs_file = FcsFile.get(experiment._id, files[0]._id)
    assert fcs_file._id == files[0]._id


def test_fcs_file_get_by_name(ligands_experiment):
    experiment, files = ligands_experiment
    fcs_file = FcsFile.get(experiment._id, name=files[0].filename)
    assert fcs_file._id == files[0]._id


def test_fcs_file_channel_for_reagent(ligands_experiment):
    _, files = ligands_experiment
    # Not a great test. This file's reagents are the same as its channels.
    assert files[0].channel_for_reagent("Time") == "Time"


def test_fcs_file_update(ligands_experiment):
    _, files = ligands_experiment
    file = files[0]
    file.filename = "new name.fcs"
    file.update()
    assert file.filename == "new name.fcs"


def test_fcs_file_get_file_internal_compensation(ligands_experiment):
    _, files = ligands_experiment
    comp = files[0].get_file_internal_compensation()
    assert type(comp) == Compensation


def test_fcs_file_get_file_internal_compensation_throws_when_no_file_internal_compensation():
    pass
    # with pytest.raises(ValueError) as err:
    #     comp = file.get_file_internal_compensation()
    # assert (
    #     err.value.args[0]
    #     == f"FCS File '{file._id}' does not have an internal compensation."
    # )


def test_fcs_file_get_events(ligands_experiment):
    _, files = ligands_experiment
    file = files[0]

    # No args
    all_events = file.get_events()
    assert type(all_events) is DataFrame

    # With subsampling
    subsampled_events = file.get_events(preSubsampleN=10, inplace=True)
    assert len(all_events) > len(subsampled_events)
    assert len(subsampled_events) == 10
    assert file._events_kwargs == {"preSubsampleN": 10}

    # inplace=True
    file.get_events(preSubsampleN=10, inplace=True)
    assert len(file.events) == 10


def test_fcs_file_get_events_with_destination(ligands_experiment, tmp_path):
    _, files = ligands_experiment
    file = files[0]

    file.get_events(destination=tmp_path / "test.fcs")

    with open(tmp_path / "test.fcs", "rb") as f:
        assert f.read()  # TODO better test


def test_fcs_file_upload(blank_experiment):
    file1 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
    )
    assert file1.filename == "Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"


def test_fcs_file_create_concatenate(ligands_experiment):
    experiment, files = ligands_experiment
    f = FcsFile.create(experiment._id, [files[0]._id, files[1]._id], "concat.fcs")
    assert f.data.get("sourceFiles") == [
        {"experimentId": experiment._id, "_id": files[0]._id},
        {"experimentId": experiment._id, "_id": files[1]._id},
    ]


def test_fcs_file_create_from_s3(blank_experiment):
    if not "S3_ACCESS_KEY" in os.environ:
        pytest.skip(
            "Skipping S3 tests. Set S3_ACCESS_KEY and S3_SECRET_KEY to run them."
        )

    s3_dict = {
        "host": "ce-test-s3-a.s3.us-east-2.amazonaws.com",
        "path": "/Specimen_001_A6_A06.fcs",
        "access_key": os.environ.get("S3_ACCESS_KEY"),
        "secret_key": os.environ.get("S3_SECRET_KEY"),
    }

    file = FcsFile.create(
        blank_experiment._id,
        s3_dict,
        "new name",
    )
    assert file.size == 22625


def test_fcs_file_create_from_dataframe(blank_experiment: Experiment):
    df = pandas.DataFrame(
        {"Chan1": [1.0, 2.0, 3.0, 4.0], "Chan2": [10.0, 20.0, 30.0, 40.0]},
        dtype="float32",
    )
    reagents = ["Reag1", "Reag2"]

    created = FcsFile.create_from_dataframe(
        blank_experiment._id,
        filename="New file.fcs",
        df=df,
        reagents=reagents,
        headers={
            "$P1D": "Linear,0,10",
            "$P2D": "Logarithmic,3,0.1",
            "Not a standard key": "a/B",
        },
    )

    assert created.filename == "New file.fcs"
    assert created.experiment_id == blank_experiment._id
    assert created.header["$PAR"] == "2"
    assert created.header["$TOT"] == "4"
    assert created.header["$P1N"] == "Chan1"
    assert created.header["$P1S"] == "Reag1"
    assert created.header["$P1E"] == "0,0"
    assert created.header["$P1D"] == "Linear,0,10"
    assert created.header["$P2N"] == "Chan2"
    assert created.header["$P2S"] == "Reag2"
    assert created.header["$P2E"] == "0,0"
    assert created.header["$P2D"] == "Logarithmic,3,0.1"
    assert (
        created.header["$COM"]
        == f"Created by the CellEngine Python Toolkit v{cellengine.__version__}"
    )
    # TODO FlowIO upper-cases all keys
    assert created.header["NOT A STANDARD KEY"] == "a/B"
    # assert parsed_header["Not a standard key"] == "a/B"


def test_fcs_file_create_from_dataframe_multiindex(blank_experiment: Experiment):
    df = pandas.DataFrame(
        [[1.0, 10.0, 1], [2.0, 20.0, 2], [3.0, 30.0, 3], [4.0, 40.0, 4]],
        columns=[["Ax488-A", "PE-A", "Cluster ID"], ["CD3", "CD4", None]],
        dtype="float32",
    )
    created = FcsFile.create_from_dataframe(
        blank_experiment._id, "myfile.fcs", df, headers={"$P3D": "Linear,0,10"}
    )

    assert created.experiment_id == blank_experiment._id
    assert created.header["$PAR"] == "3"
    assert created.header["$TOT"] == "4"
    assert created.header["$P1N"] == "Ax488-A"
    assert created.header["$P1S"] == "CD3"
    assert created.header["$P2N"] == "PE-A"
    assert created.header["$P2S"] == "CD4"
    assert created.header["$P3N"] == "Cluster ID"
    assert "$P3S" not in created.header
    assert created.header["$P3D"] == "Linear,0,10"


def test_fcs_file_create_from_dataframe_strings(blank_experiment: Experiment):
    df = pandas.DataFrame(
        [
            [1.0, "T cell", 1],
            [2.0, "T cell", 2],
            [3.0, "B cell", 3],
            [4.0, "T cell", 4],
        ],
        columns=["Ax488-A", "Cell Type", "Cluster ID"],
    )
    df["Cell Type"], cell_type_index = pandas.factorize(df["Cell Type"])
    created = FcsFile.create_from_dataframe(
        blank_experiment._id,
        "myfile.fcs",
        df,
        headers={"$P2D": "Linear,0,10", "$P3D": "Linear,0,10"},
    )

    assert created.experiment_id == blank_experiment._id
    assert created.header["$PAR"] == "3"
    assert created.header["$TOT"] == "4"
    assert created.header["$P1N"] == "Ax488-A"
    assert created.header["$P2N"] == "Cell Type"
    assert created.header["$P3N"] == "Cluster ID"
    assert created.header["$P3D"] == "Linear,0,10"


def test_fcs_file_delete(ligands_experiment):
    experiment, files = ligands_experiment
    files[0].delete()
    with pytest.raises(APIError):
        FcsFile.get(experiment._id, files[0]._id)


def test_fcs_file_plot(ligands_experiment: Tuple[Experiment, List[FcsFile]]):
    _, fcs_files = ligands_experiment
    fcs_file = fcs_files[0]
    plot = fcs_file.plot(
        "dot",
        fcs_file.channels[0],
        fcs_file.channels[1],
    )
    assert plot.fcs_file_id == fcs_file._id
    assert plot.x_channel == fcs_file.channels[0]
    assert plot.y_channel == fcs_file.channels[1]
    assert plot.plot_type == "dot"
    assert plot.population_id == None
