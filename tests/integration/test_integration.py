import os
import pytest
import pandas
import uuid
import json

from typing import Iterator

import cellengine
from cellengine.utils.api_client.APIClient import APIClient
from cellengine.utils.api_client.APIError import APIError
from cellengine.resources.attachment import Attachment
from cellengine.resources.compensation import Compensation
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.gate import (
    RangeGate,
    QuadrantGate,
    SplitGate,
    Gate,
)
from cellengine.utils.complex_population_builder import ComplexPopulationBuilder


@pytest.fixture(scope="module")
def run_id() -> str:
    return uuid.uuid4().hex[:5]


@pytest.fixture(scope="module")
def client() -> APIClient:
    username = os.environ.get("CELLENGINE_USERNAME", "gegnew")
    password = os.environ.get("CELLENGINE_PASSWORD", "testpass1")
    return APIClient(username=username, password=password)


@pytest.fixture()
def blank_experiment(run_id: str, client: APIClient) -> Iterator[Experiment]:
    exp_name = f"Ligands {run_id}"
    print(f"Setting up CellEngine experiment {exp_name}")
    exp = Experiment.create(exp_name)

    yield exp

    print(f"Starting teardown of {exp_name}")
    client.delete_experiment(exp._id)


@pytest.fixture()
def setup_experiment(blank_experiment: Experiment) -> Iterator[Experiment]:
    blank_experiment.upload_fcs_file("tests/data/Acea - Novocyte.fcs")

    yield blank_experiment


@pytest.fixture()
def ligands_experiment(
    blank_experiment: Experiment, client: APIClient
) -> Iterator[Experiment]:
    blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
    )
    blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A2_A02_MeOHperm(DL350neg).fcs"
    )

    yield blank_experiment


def test_experiment_attachments(blank_experiment: Experiment, client: APIClient):
    # POST
    blank_experiment.upload_attachment("tests/data/text.txt")
    blank_experiment.upload_attachment("tests/data/text.txt", filename="text2.txt")

    # GET
    attachments = blank_experiment.attachments
    assert all([type(a) is Attachment for a in attachments])
    assert len(attachments) == 2
    assert blank_experiment.download_attachment(name="text2.txt") == b"hello world\n\n"
    att1 = blank_experiment.get_attachment(name="text.txt")
    blank_experiment.get_attachment(_id=blank_experiment.attachments[1]._id)

    # UPDATE
    att1.filename = "newname.txt"
    att1.update()
    assert (
        blank_experiment.download_attachment(name="newname.txt") == b"hello world\n\n"
    )

    # DELETE
    [a.delete() for a in blank_experiment.attachments]
    assert len(blank_experiment.attachments) == 0


def test_fcs_file_events(ligands_experiment: Experiment):
    file = ligands_experiment.fcs_files[0]

    all_events = file.events
    limited_events = file.get_events(preSubsampleN=10)

    assert len(all_events) > len(limited_events)
    assert len(limited_events) == 10

    # it should update the events value
    file.get_events(preSubsampleN=10, inplace=True)
    assert len(file.events) == 10


def test_apply_compensations(setup_experiment: Experiment):
    # POST
    file1 = setup_experiment.fcs_files[0]
    setup_experiment.create_compensation("test_comp", file1.channels[0:2], [1, 2, 3, 4])

    # GET
    compensations = setup_experiment.compensations
    assert all([type(c) is Compensation for c in compensations])
    comp = compensations[0]
    assert comp.name == "test_comp"

    # UPDATE
    comp.name = "new_name"
    comp.update()
    comp = setup_experiment.get_compensation(name="new_name")

    # Additional functionality
    events_df = comp.apply(file1, preSubsampleN=100)
    assert len(events_df) == 100
    assert type(comp.dataframe) == pandas.DataFrame

    # with inplace=True it should save results to the target FcsFile
    comp.apply(file1, inplace=True, preSubsampleN=10)
    # TODO assert

    # DELETE
    setup_experiment.compensations[0].delete()
    assert setup_experiment.compensations == []


def test_apply_file_internal_compensation(setup_experiment: Experiment):
    file = setup_experiment.fcs_files[0]
    comp = file.get_file_internal_compensation()

    events_df = comp.apply(file, preSubsampleN=100)

    assert len(events_df) == 100
    assert type(comp.dataframe) == pandas.DataFrame

    assert all([c in events_df.columns for c in comp.channels])


def test_experiment(client: APIClient):
    experiment_name = uuid.uuid4().hex

    # POST
    exp = cellengine.Experiment.create(experiment_name)
    exp.upload_fcs_file("tests/data/Acea - Novocyte.fcs")

    # GET
    experiments = client.get_experiments()
    assert all([type(exp) is Experiment for exp in experiments])
    exp2 = client.get_experiment(name=experiment_name)

    # UPDATE
    clone = exp2.clone()
    clone.name = "edited_experiment"
    clone.update()
    assert clone.name == "edited_experiment"

    # DELETE
    client.delete_experiment(exp._id)
    client.delete_experiment(clone._id)
    with pytest.raises(APIError):
        client.get_experiment(exp._id)


def test_experiment_fcs_files(setup_experiment: Experiment, client: APIClient):
    # GET
    files = setup_experiment.fcs_files
    assert all([type(f) is FcsFile for f in files])

    # Create by copying another file in the same experiment.
    file2 = FcsFile.create(
        setup_experiment._id,
        fcs_files=files[0]._id,
        filename="new_fcs_file.fcs",
        pre_subsample_n=10,
    )

    # UPDATE
    file2.filename = "renamed.fcs"
    file2.update()
    file = setup_experiment.get_fcs_file(name="renamed.fcs")
    assert file._id == file2._id

    # events
    events_df = file.get_events(preSubsampleN=10, seed=7)
    assert len(events_df) == 10

    # DELETE
    file.delete()
    with pytest.raises(APIError):
        client.get_fcs_file(setup_experiment._id, file._id)


def test_experiment_gates(setup_experiment: Experiment):
    fcs_file = setup_experiment.fcs_files[0]

    # CREATE
    split_gate = SplitGate.create(
        setup_experiment._id,
        fcs_file.channels[0],
        "split_gate",
        2300000,
        250000,
        create_population=False,
    )
    range_gate = RangeGate.create(
        setup_experiment._id,
        fcs_file.channels[0],
        "range_gate",
        2100000,
        2500000,
        create_population=False,
    )

    # UPDATE
    Gate.update_gate_family(
        setup_experiment._id,
        split_gate.gid,
        body={"name": "new split gate name"},
    )
    assert setup_experiment.gates[0].name == "new split gate name"

    # DELETE
    range_gate.delete()
    assert len(setup_experiment.gates) == 1

    setup_experiment.delete_gate(gid=split_gate.gid)
    assert setup_experiment.gates == []


def test_apply_tailoring(ligands_experiment: Experiment):
    fcs_files = ligands_experiment.fcs_files

    # Global
    global_gate, pop = ligands_experiment.create_rectangle_gate(
        x_channel=fcs_files[0].channels[0],
        y_channel=fcs_files[0].channels[0],
        name="gate 1",
        x1=10,
        y1=10,
        x2=20,
        y2=20,
        create_population=True,
        tailored_per_file=True,
        fcs_file_id=None,
    )
    print(global_gate.model)

    # Tailored to f1
    f1_gate = ligands_experiment.create_rectangle_gate(
        x_channel=fcs_files[0].channels[0],
        y_channel=fcs_files[0].channels[0],
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

    # Apply to f2 should insert a gate for that file
    tailored1 = f1_gate.apply_tailoring([fcs_files[1]._id])
    assert len(tailored1.inserted) == 1
    assert len(tailored1.updated) == 0
    assert len(tailored1.deleted) == 0
    assert tailored1.inserted[0].fcs_file_id == fcs_files[1]._id
    print(tailored1.inserted[0].model)

    # Apply global to f2 should delete f2's tailored gate
    print(global_gate.model)
    tailored2 = global_gate.apply_tailoring([fcs_files[1]._id])
    assert len(tailored2.inserted) == 0
    assert len(tailored2.updated) == 0
    assert len(tailored2.deleted) == 1
    assert tailored2.deleted[0] == tailored1.inserted[0]._id


def test_experiment_populations(setup_experiment: Experiment, client: APIClient):
    fcs_file = setup_experiment.fcs_files[0]

    # GET
    quad_gate, quad_pops = QuadrantGate.create(
        setup_experiment._id,
        fcs_file.channels[0],
        fcs_file.channels[1],
        "quadrant_gate",
        2300000,
        250000,
    )

    split_gate, split_pops = SplitGate.create(
        setup_experiment._id, fcs_file.channels[0], "split gate", 2300000, 250000
    )
    assert ["split gate (L)", "split gate (R)"] == [p.name for p in split_pops]

    # CREATE
    complex_payload = (
        ComplexPopulationBuilder("complex pop")
        .Or([quad_gate.model["gids"][0], quad_gate.model["gids"][2]])
        .build()
    )
    client.post_population(setup_experiment._id, complex_payload)
    complex_pop = [p for p in setup_experiment.populations if "complex pop" in p.name][
        0
    ]

    # UPDATE
    complex_pop.name = "my new name"
    complex_pop.update()
    assert complex_pop.name == "my new name"

    # DELETE
    complex_pop.delete()
    assert "complex pop" not in [p.name for p in setup_experiment.populations]


def test_create_new_fcsfile_from_s3(blank_experiment: Experiment):
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


def test_create_new_fcsfile_from_dataframe(blank_experiment: Experiment):
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
    parsed_header = json.loads(created.header)  # type: ignore - might be none
    assert parsed_header["$PAR"] == "2"
    assert parsed_header["$TOT"] == "4"
    assert parsed_header["$P1N"] == "Chan1"
    assert parsed_header["$P1S"] == "Reag1"
    assert parsed_header["$P1E"] == "0,0"
    assert parsed_header["$P1D"] == "Linear,0,10"
    assert parsed_header["$P2N"] == "Chan2"
    assert parsed_header["$P2S"] == "Reag2"
    assert parsed_header["$P2E"] == "0,0"
    assert parsed_header["$P2D"] == "Logarithmic,3,0.1"
    assert (
        parsed_header["$COM"]
        == f"Created by the CellEngine Python Toolkit v{cellengine.__version__}"
    )
    # TODO FlowIO upper-cases all keys
    assert parsed_header["NOT A STANDARD KEY"] == "a/B"
    # assert parsed_header["Not a standard key"] == "a/B"


def test_create_new_fcsfile_from_dataframe_multiindex(blank_experiment: Experiment):
    df = pandas.DataFrame(
        [[1.0, 10.0, 1], [2.0, 20.0, 2], [3.0, 30.0, 3], [4.0, 40.0, 4]],
        columns=[["Ax488-A", "PE-A", "Cluster ID"], ["CD3", "CD4", None]],
        dtype="float32",
    )
    created = FcsFile.create_from_dataframe(
        blank_experiment._id, "myfile.fcs", df, headers={"$P3D": "Linear,0,10"}
    )

    assert created.experiment_id == blank_experiment._id
    parsed_header = json.loads(created.header)  # type: ignore - might be none
    assert parsed_header["$PAR"] == "3"
    assert parsed_header["$TOT"] == "4"
    assert parsed_header["$P1N"] == "Ax488-A"
    assert parsed_header["$P1S"] == "CD3"
    assert parsed_header["$P2N"] == "PE-A"
    assert parsed_header["$P2S"] == "CD4"
    assert parsed_header["$P3N"] == "Cluster ID"
    assert "$P3S" not in parsed_header
    assert parsed_header["$P3D"] == "Linear,0,10"


def test_create_new_fcsfile_from_dataframe_strings(blank_experiment: Experiment):
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
    parsed_header = json.loads(created.header)  # type: ignore - might be none
    assert parsed_header["$PAR"] == "3"
    assert parsed_header["$TOT"] == "4"
    assert parsed_header["$P1N"] == "Ax488-A"
    assert parsed_header["$P2N"] == "Cell Type"
    assert parsed_header["$P3N"] == "Cluster ID"
    assert parsed_header["$P3D"] == "Linear,0,10"
