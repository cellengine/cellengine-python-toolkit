import uuid
import pytest
from typing import Iterator
from datetime import datetime

from cellengine.resources.folder import Folder


@pytest.fixture()
def empty_folder(client) -> Iterator[Folder]:
    suffix = uuid.uuid4().hex
    folder = client.post_folder({"name": f"Test folder {suffix}"})

    yield folder


# Begin tests


def test_folder_get(empty_folder: Folder):
    folder_by_id = Folder.get(empty_folder._id)
    assert type(folder_by_id) is Folder

    folder_by_name = Folder.get(name=empty_folder.name)
    assert type(folder_by_name) is Folder


def test_folder_create():
    folder_name = uuid.uuid4().hex
    folder = Folder.create(folder_name)
    assert type(folder._id) is str
    assert folder.name == folder_name
    assert type(folder.created) is datetime
    assert folder.deleted is None
    assert type(folder.creator) is str
    assert folder.path == []
    assert folder.permissions[0].get("grantee").get("_id") == folder.creator  # type: ignore


def test_folder_update(empty_folder: Folder):
    assert empty_folder.name != "new name"
    empty_folder.name = "new name"
    empty_folder.update()
    assert empty_folder.name == "new name"


def test_folder_delete(empty_folder: Folder):
    empty_folder.delete()
    assert type(empty_folder.deleted) is datetime


def test_folder_undelete(empty_folder: Folder):
    empty_folder.delete()
    assert type(empty_folder.deleted) is datetime
    empty_folder.undelete()
    assert empty_folder.deleted is None
