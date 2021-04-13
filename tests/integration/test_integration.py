import pytest
import pandas

import cellengine
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
def client():
    return cellengine.APIClient("gegnew", "testpass123")


@pytest.fixture(scope="module")
def setup_experiment(request, client):
    print("Setting up CellEngine experiment for {}".format(__name__))
    exp = cellengine.Experiment.create("new_experiment")
    exp.upload_fcs_file("tests/data/Acea - Novocyte.fcs")

    yield exp

    print("Starting teardown of: {}".format(__name__))
    client.delete_experiment(exp._id)


def test_experiment_attachments(setup_experiment, client):
    experiment = client.get_experiment(name="new_experiment")

    # POST
    experiment.upload_attachment("tests/data/text.txt")
    experiment.upload_attachment("tests/data/text.txt", filename="text2.txt")

    # GET
    attachments = experiment.attachments
    assert all([type(a) is Attachment for a in attachments])
    assert len(attachments) == 2
    assert experiment.download_attachment(name="text2.txt") == b"hello world\n\n"
    att1 = experiment.get_attachment(name="text.txt")
    experiment.get_attachment(_id=experiment.attachments[1]._id)

    # UPDATE
    att1.filename = "newname.txt"
    att1.update()
    assert experiment.download_attachment(name="newname.txt") == b"hello world\n\n"

    # DELETE
    [a.delete() for a in experiment.attachments]
    assert len(experiment.attachments) == 0


def test_fcs_file_events(setup_experiment, client):
    experiment = client.get_experiment(name="new_experiment")
    file = experiment.fcs_files[0]

    all_events = file.events
    limited_events = file.get_events(preSubsampleN=10)

    assert len(all_events) > len(limited_events)
    assert len(limited_events) == 10

    # it should update the events value
    file.get_events(preSubsampleN=10, inplace=True)
    assert len(limited_events) == len(file.events)


def test_apply_compensations(setup_experiment, client):
    experiment = client.get_experiment(name="new_experiment")

    # POST
    file1 = experiment.fcs_files[0]
    experiment.create_compensation("test_comp", file1.channels[0:2], [1, 2, 3, 4])

    # GET
    compensations = experiment.compensations
    assert all([type(c) is Compensation for c in compensations])
    comp = compensations[0]
    assert comp.name == "test_comp"

    # UPDATE
    comp.name = "new_name"
    comp.update()
    comp = experiment.get_compensation(name="new_name")

    # Additional functionality
    events_df = comp.apply(file1, preSubsampleN=100)
    assert len(events_df) == 100
    assert type(comp.dataframe) == pandas.DataFrame

    # with inplace=True it should save results to the target FcsFile
    another_events_df = comp.apply(file1, inplace=True, preSubsampleN=10)
    file1.events == another_events_df

    # DELETE
    experiment.compensations[0].delete()
    assert experiment.compensations == []


def test_apply_file_internal_compensation(setup_experiment, client):
    experiment = client.get_experiment(name="new_experiment")

    file = experiment.fcs_files[0]
    comp = file.get_file_internal_compensation()

    events_df = comp.apply(file, preSubsampleN=100)

    assert len(events_df) == 100
    assert type(comp.dataframe) == pandas.DataFrame

    assert all([c in events_df.columns for c in comp.channels])


def test_experiment(setup_experiment, client):
    # POST
    exp = cellengine.Experiment.create("new_experiment_2")
    exp.upload_fcs_file("tests/data/Acea - Novocyte.fcs")

    # GET
    experiments = client.get_experiments()
    # assert len(experiments) == 2
    assert all([type(exp) is Experiment for exp in experiments])
    exp2 = client.get_experiment(name="new_experiment_2")

    # UPDATE
    clone = exp2.clone(name="clone")
    clone.name = "edited_experiment"
    clone.update()
    assert clone.name == "edited_experiment"

    # DELETE
    client.delete_experiment(exp._id)
    client.delete_experiment(clone._id)
    with pytest.raises(APIError):
        client.get_experiment(exp._id)


def test_experiment_fcs_files(setup_experiment, client):
    experiment = client.get_experiment(name="new_experiment")

    # GET
    files = experiment.fcs_files
    assert all([type(f) is FcsFile for f in files])

    # CREATE
    file2 = FcsFile.create(
        experiment._id,
        fcs_files=files[0]._id,
        filename="new_fcs_file.fcs",
        pre_subsample_n=10,
    )

    # UPDATE
    file2.filename = "renamed.fcs"
    file2.update()
    file = experiment.get_fcs_file(name="renamed.fcs")
    assert file._id == file2._id

    # events
    events_df = file.get_events(preSubsampleN=10, seed=7)
    assert len(events_df) == 10

    # DELETE
    file.delete()
    with pytest.raises(APIError):
        client.get_fcs_file(experiment._id, file._id)


def test_experiment_gates(setup_experiment, client):
    experiment = client.get_experiment(name="new_experiment")
    fcs_file = experiment.fcs_files[0]

    # CREATE
    split_gate = SplitGate.create(
        experiment._id, fcs_file.channels[0], "split_gate", 2300000, 250000
    )
    split_gate.post()
    range_gate = RangeGate.create(
        experiment._id, fcs_file.channels[0], "range_gate", 2100000, 2500000,
    )
    range_gate.post()

    # UPDATE
    range_gate.tailor_to(fcs_file._id)
    range_gate.update()
    assert range_gate.tailored_per_file is True
    assert range_gate.fcs_file_id == fcs_file._id

    population = experiment.populations[0]
    Gate.update_gate_family(
        experiment._id,
        split_gate.gid,
        body={"name": "new split gate name", "parentPopulationId": population._id},
    )
    assert experiment.gates[0].parent_population_id == population._id
    assert experiment.gates[0].name == "new split gate name"

    # DELETE
    range_gate.delete()
    assert len(experiment.gates) == 1

    Gate.delete_gates(experiment._id, gid=split_gate.gid)
    assert experiment.gates == []


def test_experiment_populations(setup_experiment, client):
    experiment = client.get_experiment(name="new_experiment")
    fcs_file = experiment.fcs_files[0]

    # GET
    quad_gate = QuadrantGate.create(
        experiment._id,
        fcs_file.channels[0],
        fcs_file.channels[1],
        "quadrant_gate",
        2300000,
        250000,
    )
    quad_gate.post()

    split_gate = SplitGate.create(
        experiment._id, fcs_file.channels[0], "split_gate", 2300000, 250000
    )
    split_gate.post()
    assert "split_gate (L)", "split_gate (R)" in [
        p.name for p in experiment.populations
    ]

    # CREATE
    complex_payload = (
        ComplexPopulationBuilder("complex pop")
        .Or([quad_gate.model.gids[0], quad_gate.model.gids[2]])
        .build()
    )
    client.post_population(experiment._id, complex_payload)
    complex_pop = [p for p in experiment.populations if "complex pop" in p.name][0]

    # UPDATE
    complex_pop.name = "my new name"
    complex_pop.update()
    assert complex_pop.name == "my new name"

    # DELETE
    complex_pop.delete()
    assert "complex pop" not in [p.name for p in experiment.populations]
