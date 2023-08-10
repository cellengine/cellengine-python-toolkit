import pytest
from typing import Iterator, Tuple
from datetime import datetime


from cellengine.utils.api_client.APIClient import APIClient
from cellengine.resources.attachment import Attachment
from cellengine.resources.experiment import Experiment


@pytest.fixture()
def experiment_with_attachment(
    run_id: str, client: APIClient
) -> Iterator[Tuple[Experiment, Attachment]]:
    exp_name = f"Ligands {run_id}"
    print(f"Setting up CellEngine experiment {exp_name}")
    exp = Experiment.create(exp_name)
    att = exp.upload_attachment("tests/data/text.txt")

    yield exp, att

    print(f"Starting teardown of {exp_name}")
    client.delete_experiment(exp._id)


# Begin tests


def test_attachment_get_attachment_by_name(
    experiment_with_attachment: Tuple[Experiment, Attachment]
):
    experiment, _ = experiment_with_attachment
    att = Attachment.get(experiment._id, name="text.txt")
    assert type(att) is Attachment


def test_attachment_get_attachment_by_id(
    experiment_with_attachment: Tuple[Experiment, Attachment]
):
    experiment, attachment = experiment_with_attachment
    att = Attachment.get(experiment._id, attachment._id)
    assert type(att) is Attachment


def test_experiment_upload_attachment(blank_experiment: Experiment):
    att = blank_experiment.upload_attachment("tests/data/text.txt")
    assert type(att) is Attachment
    assert hasattr(att, "_id")
    assert att.experiment_id == blank_experiment._id
    assert att.filename == "text.txt"
    assert att.md5 == "d300fa70af75aa4b157382293609dcd9"
    assert att.crc32c == "4afc08fb"
    assert att.size == 13
    assert type(att.created) is datetime


def test_upload_attachment(blank_experiment: Experiment):
    att = Attachment.upload(blank_experiment._id, "tests/data/text.txt")
    assert type(att) is Attachment
    assert hasattr(att, "_id")
    assert att.experiment_id == blank_experiment._id
    assert att.filename == "text.txt"
    assert att.md5 == "d300fa70af75aa4b157382293609dcd9"
    assert att.crc32c == "4afc08fb"
    assert att.size == 13
    assert type(att.created) is datetime


def test_update_attachment(experiment_with_attachment: Tuple[Experiment, Attachment]):
    experiment_with_attachment[1].filename = "newname.ext"
    experiment_with_attachment[1].update()
    assert experiment_with_attachment[1].filename == "newname.ext"


def test_delete_attachment(experiment_with_attachment: Tuple[Experiment, Attachment]):
    experiment, attachment = experiment_with_attachment
    attachment.delete()
    with pytest.raises(RuntimeError):
        Attachment.get(experiment._id, attachment._id)


def test_download_attachment(experiment_with_attachment: Tuple[Experiment, Attachment]):
    _, attachment = experiment_with_attachment
    content = attachment.download()
    assert content == b"hello world\n\n"
