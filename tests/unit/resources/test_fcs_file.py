from io import BufferedReader, BytesIO
import copy
import json
import os

from pandas.core.frame import DataFrame
import pytest
import responses

from cellengine.resources.compensation import Compensation
from cellengine.resources.fcs_file import FcsFile
from cellengine.utils.helpers import to_camel_case


EXP_ID = "5d38a6f79fae87499999a74b"


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


def test_channel_for_reagent(fcs_files):
    fcs_file_copy = copy.deepcopy(fcs_files[0])
    fcs_file_copy["panel"][10]["reagent"] = "Ki-67"
    fcs_file = FcsFile.from_dict(fcs_file_copy)
    assert fcs_file.channel_for_reagent("Ki-67") == "Vio585-A"


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
def test_should_update_fcs_file(ENDPOINT_BASE, client, fcs_files):
    file = FcsFile.from_dict(fcs_files[0])
    file.name = "new name"
    expected_response = fcs_files[0].copy()
    expected_response.update({"filename": "new name"})
    responses.add(
        responses.PATCH,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file._id}",
        json=expected_response,
    )
    file.update()
    assert json.loads(responses.calls[0].request.body) == file.to_dict()
    assert expected_response == file.to_dict()


@responses.activate
def test_gets_file_internal_compensation(ENDPOINT_BASE, client, fcs_files, spillstring):
    # Given: An FcsFile with a spill string
    file_data = fcs_files[0]
    file_data["spillString"] = spillstring
    file = FcsFile.from_dict(file_data)
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
def test_throws_correct_error_when_no_file_internal_compensation(
    ENDPOINT_BASE, client, fcs_files
):
    # Given: An FcsFile with no spill string
    expected_response = fcs_files[0].copy()
    file_data = fcs_files[0].copy()
    file_data["spillString"] = None
    file_data["hasFileInternalComp"] = False
    file = FcsFile.from_dict(file_data)
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file._id}",
        json=expected_response,
    )

    # When:
    with pytest.raises(ValueError) as err:
        comp = file.get_file_internal_compensation()
        # Then:
    assert (
        err.value.args[0]
        == f"FCS File '{file._id}' does not have an internal compensation."
    )


@responses.activate
def test_parses_fcs_file_events(ENDPOINT_BASE, client, fcs_files):
    file_data = fcs_files[0]
    file = FcsFile.from_dict(file_data)
    events_body = open("tests/data/Acea - Novocyte.fcs", "rb")
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file._id}.fcs",
        body=events_body,
    )

    # When:
    data = file.get_events()

    # Then:
    assert type(data) is DataFrame


@responses.activate
def test_parses_fcs_file_events_inplace(ENDPOINT_BASE, client, fcs_files):
    file_data = fcs_files[0]
    file = FcsFile.from_dict(file_data)
    events_body = open("tests/data/Acea - Novocyte.fcs", "rb")
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file._id}.fcs",
        body=events_body,
    )

    # When:
    file.get_events(inplace=True)

    # Then:
    assert type(file.events) is DataFrame


@responses.activate
def test_save_events_to_file(ENDPOINT_BASE, client, fcs_files):
    file_data = fcs_files[0]
    file = FcsFile.from_dict(file_data)
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file._id}.fcs",
        body=BufferedReader(BytesIO(b"test")),
    )

    # When:
    file.get_events(destination="test.fcs")

    # Then:
    with open("test.fcs", "r") as events:
        assert events.readline() == "test"
    os.remove("test.fcs")


@responses.activate
def test_get_events_save_kwargs(ENDPOINT_BASE, client, fcs_files):
    file_data = fcs_files[0]
    file = FcsFile.from_dict(file_data)
    events_body = open("tests/data/Acea - Novocyte.fcs", "rb")
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file._id}.fcs",
        body=events_body,
    )

    # When:
    file.get_events(inplace=True, compensatedQ=False, seed=10)

    # Then:
    assert file._events_kwargs == {"compensatedQ": False, "seed": 10}


@responses.activate
def test_create_by_uploading(ENDPOINT_BASE, fcs_files):
    """Test upload of a new fcs_file.
    This test must be run from the project root directory"""
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/fcsfiles",
        json=fcs_files[1],
    )
    FcsFile.create(EXP_ID, [fcs_files[0]["_id"]], "new file")
    assert json.loads(responses.calls[0].request.body) == {
        "fcsFiles": ["5d64abe2ca9df61349ed8e79"],
        "filename": "new file",
    }


@responses.activate
def test_create_from_s3(ENDPOINT_BASE, client, fcs_files):
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/fcsfiles",
        json=fcs_files[1],
    )

    s3_dict = {
        "host": "ce-test-s3-a.s3.us-east-2.amazonaws.com",
        "path": "/Specimen_001_A6_A06.fcs",
        "access_key": os.environ.get("S3_ACCESS_KEY"),
        "secret_key": os.environ.get("S3_SECRET_KEY"),
    }

    FcsFile.create(
        EXP_ID,
        s3_dict,
        "new name",
    )
    payload = json.loads(responses.calls[0].request.body)["fcsFiles"][0]  # type: ignore

    assert {"host", "path", "accessKey", "secretKey"} <= payload.keys()
    assert payload == {to_camel_case(k): v for k, v in s3_dict.items()}


@responses.activate
def test_create_from_another_experiment(ENDPOINT_BASE, client, fcs_files):
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/fcsfiles",
        json=fcs_files[1],
    )

    file_dict = {
        "_id": fcs_files[1]["_id"],
        "experiment_id": EXP_ID,
    }

    FcsFile.create(
        EXP_ID,
        file_dict,
        "new name",
    )
    payload = json.loads(responses.calls[0].request.body)  # type: ignore

    assert {"_id", "experimentId"} <= payload["fcsFiles"][0].keys()


EXP_ID = "5d38a6f79fae87499999a74b"
FCSFILE_ID = "5d64abe2ca9df61349ed8e7c"
params = [
    # (request, expected response)
    (FCSFILE_ID, [FCSFILE_ID]),
    ([FCSFILE_ID], [FCSFILE_ID]),
    (
        [
            "5d64abe2ca9df61349ed8e7a",
            "5d64abe2ca9df61349ed8e7b",
            "5d64abe2ca9df61349ed8e7c",
        ],
        [
            "5d64abe2ca9df61349ed8e7a",
            "5d64abe2ca9df61349ed8e7b",
            "5d64abe2ca9df61349ed8e7c",
        ],
    ),
    (
        {"experiment_id": EXP_ID, "_id": FCSFILE_ID},
        [{"experimentId": EXP_ID, "_id": FCSFILE_ID}],
    ),
    (
        {
            "host": "ce-test-s3-a.s3.us-east-2.amazonaws.com",
            "path": "/Specimen_001_A6_A06.fcs",
        },
        [
            {
                "host": "ce-test-s3-a.s3.us-east-2.amazonaws.com",
                "path": "/Specimen_001_A6_A06.fcs",
            }
        ],
    ),
]


@pytest.mark.parametrize("fcs_file_args,expected_response", params)
@responses.activate
def test_should_create_fcs_file_and_correctly_parse_fcs_file_args(
    ENDPOINT_BASE, client, fcs_files, fcs_file_args, expected_response
):
    """Test upload of a new fcs_file.
    This test must be run from the project root directory"""
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/fcsfiles",
        json=fcs_files[1],
    )
    FcsFile.create(EXP_ID, fcs_file_args, "new file")
    assert json.loads(responses.calls[0].request.body) == {
        "fcsFiles": expected_response,
        "filename": "new file",
    }


@responses.activate
def test_should_create_fcs_file_and_correctly_parse_body_args(
    ENDPOINT_BASE, client, fcs_files
):
    """Test upload of a new fcs_file.
    This test must be run from the project root directory"""
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/fcsfiles",
        json=fcs_files[1],
    )
    FcsFile.create(
        EXP_ID,
        FCSFILE_ID,
        "new name",
        add_file_number=True,
        add_event_number=True,
        pre_subsample_n=1,
        pre_subsample_p=1,
    )
    assert json.loads(responses.calls[0].request.body) == {
        "fcsFiles": [FCSFILE_ID],
        "filename": "new name",
        "addFileNumber": True,
        "addEventNumber": True,
        "preSubsampleN": 1,
        "preSubsampleP": 1
        # leave out "seed" to test param not specified
    }


@responses.activate
def test_should_delete_fcs_file(ENDPOINT_BASE, client, fcs_files):
    fcs_file = FcsFile.from_dict(fcs_files[0])
    responses.add(
        responses.DELETE,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/fcsfiles/{fcs_file._id}",
    )
    deleted = fcs_file.delete()
    assert deleted is None
