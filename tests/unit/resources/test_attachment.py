import os
import json
from pathlib import Path
import pytest
import responses
import cellengine


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@pytest.fixture(scope="module")
def attachment(experiment, attachments):
    with responses.RequestsMock() as resps:
        resps.add(
            responses.GET,
            base_url + "experiments/5d38a6f79fae87499999a74b/attachments",
            json=attachments,
        )
        return experiment.attachments[0]


def attachments_tester(attachment):
    assert type(attachment._properties) is dict
    assert type(attachment) is cellengine.Attachment
    assert hasattr(attachment, "experiment_id")
    assert hasattr(attachment, "filename")
    assert hasattr(attachment, "md5")
    assert hasattr(attachment, "crc32c")
    assert hasattr(attachment, "size")


@responses.activate
def test_list_attachments(experiment, attachments):
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/attachments",
        json=attachments,
    )
    att = experiment.attachments
    assert type(att) is list
    [attachments_tester(item) for item in att]


@responses.activate
def test_get_attachment(experiment, attachments):
    responses.add(
        responses.GET,
        base_url + "experiments/5d64abe2ca9df61349ed8e78/attachments",
        json=attachments,
    )
    att = cellengine.Attachment.list('5d64abe2ca9df61349ed8e78')
    assert type(att) is list
    [attachments_tester(item) for item in att]


@responses.activate
def test_delete_attachment(experiment, attachment, attachments):
    responses.add(
        responses.DELETE,
        base_url
        + "experiments/5e26b3f94b14014f02b1ecda/attachments/{0}".format(attachment._id),
        status=204,
    )
    delete_attachment = attachment.delete()
    assert delete_attachment is None


@responses.activate
def test_update_attachment(experiment, attachment, attachments):
    """Test that the .update() method makes the correct call. Does not test
    that the correct response is made; this should be done with an integration
    test.
    """
    # patch the mocked response with the correct values
    response = attachment._properties.copy()
    response.update({"filename": "newname.file"})
    responses.add(
        responses.PATCH,
        base_url
        + "experiments/5e26b3f94b14014f02b1ecda/attachments/{0}".format(attachment._id),
        json=response,
    )
    attachment.filename = "newname.file"
    attachment.update()
    attachments_tester(attachment)
    assert json.loads(responses.calls[0].request.body) == attachment._properties


@responses.activate
def test_download_attachment(experiment, attachment):
    responses.add(
        responses.GET,
        base_url
        + "experiments/5e26b3f94b14014f02b1ecda/attachments/{0}".format(attachment._id),
        json="some file content",
    )
    _file = attachment.download()
    assert _file == "some file content"


@responses.activate
def test_create_attachment(experiment, attachments):
    """Test creation of a new attachment.
    This test must be run from the project root directory"""
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/attachments",
        json=attachments[0],
    )
    att = cellengine.Attachment.create(experiment._id, "tests/data/text.txt")
    attachments_tester(att)
