import json
import pytest
import responses
from cellengine.resources.attachment import Attachment


EXP_ID = "5d38a6f79fae87499999a74b"


@pytest.fixture(scope="module")
def attachment(ENDPOINT_BASE, client, attachments):
    att = attachments[0]
    att.update({"experimentId": EXP_ID})
    return Attachment.from_dict(att)


def attachments_tester(attachment):
    assert type(attachment) is Attachment
    assert hasattr(attachment, "experiment_id")
    assert hasattr(attachment, "filename")
    assert hasattr(attachment, "md5")
    assert hasattr(attachment, "crc32c")
    assert hasattr(attachment, "size")


@responses.activate
def test_should_get_attachment(ENDPOINT_BASE, attachment):
    responses.add(
        responses.GET,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/attachments",
        json=[attachment.to_dict()],
    )
    att = Attachment.get(EXP_ID, attachment._id)
    attachments_tester(att)


@responses.activate
def test_should_create_attachment(ENDPOINT_BASE, experiment, attachments):
    """Test creation of a new attachment.
    This test must be run from the project root directory"""
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/attachments",
        json=attachments[0],
    )
    att = Attachment.upload(experiment._id, "tests/data/text.txt")
    attachments_tester(att)


@responses.activate
def test_should_delete_attachment(ENDPOINT_BASE, attachment):
    responses.add(
        responses.DELETE,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/attachments/{attachment._id}",
    )
    delete_attachment = attachment.delete()
    assert delete_attachment is None


@responses.activate
def test_update_attachment(ENDPOINT_BASE, experiment, attachment, attachments):
    """Test that the .update() method makes the correct call. Does not test
    that the correct response is made; this should be done with an integration
    test.
    """
    # patch the mocked response with the correct values
    expected_resp = attachment.to_dict().copy()
    expected_resp.update({"filename": "newname.file"})
    responses.add(
        responses.PATCH,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/attachments/{attachment._id}",
        json=expected_resp,
    )
    attachment.filename = "newname.file"
    attachment.update()
    attachments_tester(attachment)
    assert json.loads(responses.calls[0].request.body) == attachment.to_dict()  # type: ignore


@responses.activate
def test_download_attachment(ENDPOINT_BASE, experiment, attachment):
    responses.add(
        responses.GET,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/attachments/{attachment._id}",
        json="some file content",
    )
    _file = attachment.download()
    assert _file == b'"some file content"'
