import os
import json
import pytest
import responses
from io import BufferedReader, BytesIO

from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.compensation import Compensation
from cellengine.utils.converter import converter


EXP_ID = "5d38a6f79fae87499999a74b"


@pytest.fixture(scope="function")
def fcs_file(ENDPOINT_BASE, client, fcs_files):
    file = fcs_files[0]
    file.update({"experimentId": EXP_ID})
    return converter.structure(file, FcsFile)


@responses.activate
def test_get_fcs_file(ENDPOINT_BASE, client, fcs_files):
    file_id = fcs_files[0]["_id"]
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file_id}",
        json=fcs_files[0],
    )
    fcs_file = client.get_fcs_file(experiment_id=EXP_ID, _id=file_id)
    assert fcs_file._id == file_id


@responses.activate
def test_get_fcs_file_by_name(ENDPOINT_BASE, client, fcs_files):
    file_id = fcs_files[3]["_id"]
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles",
        json=fcs_files[3],
    )
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file_id}",
        json=fcs_files[3],
    )
    fcs_file = client.get_fcs_file(
        experiment_id="5d38a6f79fae87499999a74b", name="Specimen_001_A1_A01.fcs"
    )
    assert fcs_file._id == file_id


@responses.activate
def test_should_update_fcs_file(ENDPOINT_BASE, client, fcs_file, fcs_files):
    fcs_file.name = "new name"
    expected_response = fcs_files[0].copy()
    expected_response.update({"filename": "new name"})
    responses.add(
        responses.PATCH,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{fcs_file._id}",
        json=expected_response,
    )
    fcs_file.update()
    assert json.loads(
        responses.calls[0].request.body  # type: ignore
    ) == converter.unstructure(fcs_file)
    assert converter.structure(expected_response, FcsFile) == fcs_file


@responses.activate
def test_gets_file_internal_compensation(ENDPOINT_BASE, client, fcs_files, spillstring):
    # Given: An FcsFile with a spill string
    file_data = fcs_files[0]
    file_data["spillString"] = spillstring
    file = converter.structure(file_data, FcsFile)
    expected_response = fcs_files[0].copy()
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file._id}",
        json=expected_response,
    )

    # When:
    comp = file.get_file_internal_compensation()

    # Then:
    assert type(comp) == Compensation


@responses.activate
def test_save_events_to_file(ENDPOINT_BASE, client, fcs_file):
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{fcs_file._id}.fcs",
        body=BufferedReader(BytesIO(b"test")),  # type: ignore
    )

    # When:
    fcs_file.get_events(destination="test.fcs")

    # Then:
    with open("test.fcs", "r") as events:
        assert events.readline() == "test"
    os.remove("test.fcs")


@responses.activate
def test_updates_annotations(ENDPOINT_BASE, client, fcs_file, fcs_files):
    new_annotation = [{"value": "some value", "name": "some name"}]
    expected_response = fcs_files[0]
    expected_response.update({"annotations": new_annotation})
    responses.add(
        responses.PATCH,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{fcs_file._id}",
        json=expected_response,
    )

    # When:
    fcs_file.annotations = new_annotation
    fcs_file.update()

    # Then:
    assert fcs_file.annotations == new_annotation


def test_errors_when_bad_annotations_added(fcs_file, fcs_files):
    new_annotation = [{"value": "some value", "name": "some name"}]
    expected_response = fcs_files[0]
    expected_response.update({"annotations": new_annotation})

    with pytest.raises(TypeError):
        fcs_file.annotations = "something wrong"
