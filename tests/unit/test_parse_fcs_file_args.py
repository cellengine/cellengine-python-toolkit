import os
import json
import pytest
import responses
import cellengine
from cellengine import helpers


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@responses.activate
def test_fcs_file_and_fcs_file_id_defined(experiment, experiments, gates):
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=201,
        json=gates[0],
    )
    with pytest.raises(ValueError):
        experiment.create_rectangle_gate(
            "FSC-A",
            "FSC-W",
            "fcs_rect_gate",
            x1=1,
            x2=2,
            y1=3,
            y2=4,
            fcs_file="Specimen_001_A1_A01.fcs",
            fcs_file_id="5d38a7159fae87499999a74e",
            tailored_per_file=True,
        )


@responses.activate
def test_tailored_per_file_true(experiment, gates):
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=201,
        json=gates[0],
    )
    res = experiment.create_rectangle_gate(
        "FSC-A",
        "FSC-W",
        "fcs_rect_gate",
        x1=1,
        x2=2,
        y1=3,
        y2=4,
        tailored_per_file=True,
    )
    res.post()
    assert json.loads(responses.calls[0].request.body)["tailoredPerFile"] == True


@responses.activate
def test_fcs_file_id_is_None_and_fcs_file_is_None(experiment, gates):
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=201,
        json=gates[0],
    )
    res = experiment.create_rectangle_gate(
        "FSC-A", "FSC-W", "fcs_rect_gate", x1=1, x2=2, y1=3, y2=4
    )
    res.post()
    assert json.loads(responses.calls[0].request.body)["fcsFileId"] == None


@responses.activate
def test_create_global_tailored_gate(experiment, gates):
    global_gid = helpers.generate_id()
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=201,
        json=gates[0],
    )
    res = experiment.create_rectangle_gate(
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="fcs_rect_gate",
        x1=1,
        x2=2,
        y1=3,
        y2=4,
        tailored_per_file=True,
        gid=global_gid,
    )
    res.post()
    assert json.loads(responses.calls[0].request.body)["tailoredPerFile"] == True
    assert json.loads(responses.calls[0].request.body)["gid"] == global_gid


@responses.activate
def test_specify_fcs_file_id(experiment, gates):
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=201,
        json=gates[0],
    )
    res = experiment.create_rectangle_gate(
        x_channel="FSC-A",
        y_channel="FSC-W",
        name="fcs_rect_gate",
        x1=1,
        x2=2,
        y1=3,
        y2=4,
        fcs_file_id="5d38a7159fae87499999a751",
        tailored_per_file=True,
    )
    res.post()
    assert (
        json.loads(responses.calls[0].request.body)["fcsFileId"]
        == "5d38a7159fae87499999a751"
    )


@responses.activate
def test_fcs_file_called_by_name(experiment, fcsfiles, gates):
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/fcsfiles",
        json=[fcsfiles[3]],
    )
    responses.add(
        responses.GET,
        base_url
        + "experiments/5d38a6f79fae87499999a74b/fcsfiles/5d64abe2ca9df61349ed8e7c",
        json=fcsfiles[3],
    )
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        status=201,
        json=gates[0],
    )
    res = experiment.create_rectangle_gate(
        "FSC-A",
        "FSC-W",
        "fcs_rect_gate",
        x1=1,
        x2=2,
        y1=3,
        y2=4,
        fcs_file="Specimen_001_A1_A01.fcs",
        tailored_per_file=True,
    )
    res.post()
    assert json.loads(responses.calls[2].request.body)["tailoredPerFile"] == True
    assert (
        json.loads(responses.calls[2].request.body)["fcsFileId"]
        == "5d64abe2ca9df61349ed8e7c"
    )
