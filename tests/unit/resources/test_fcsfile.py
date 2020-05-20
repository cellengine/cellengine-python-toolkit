import json
import responses
from cellengine.resources.fcsfile import FcsFile


EXP_ID = "5d38a6f79fae87499999a74b"


@responses.activate
def test_get_fcsfile(ENDPOINT_BASE, client, fcsfiles):
    file_id = fcsfiles[0]["_id"]
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file_id}",
        json=fcsfiles[0],
    )
    fcsfile = client.get_fcsfile(experiment_id=EXP_ID, _id=file_id)
    assert fcsfile._id == file_id


@responses.activate
def test_get_fcsfile_by_name(ENDPOINT_BASE, client, fcsfiles):
    file_id = fcsfiles[3]["_id"]
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles",
        json=fcsfiles[3],
    )
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file_id}",
        json=fcsfiles[3],
    )
    fcsfile = client.get_fcsfile(
        experiment_id="5d38a6f79fae87499999a74b", name="Specimen_001_A1_A01.fcs"
    )
    assert fcsfile._id == file_id


@responses.activate
def test_should_update_fcsfile(ENDPOINT_BASE, client, fcsfiles):
    file = FcsFile(fcsfiles[0])
    file.name = "new name"
    expected_response = fcsfiles[0].copy()
    expected_response.update({"filename": "new name"})
    responses.add(
        responses.PATCH,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file._id}",
        json=expected_response,
    )
    file.update()
    assert json.loads(responses.calls[0].request.body) == file._properties
    assert expected_response == file._properties
