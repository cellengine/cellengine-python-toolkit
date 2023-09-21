from __future__ import annotations
from typing import Optional, Any, Dict, List, Union
from datetime import datetime
import cellengine as ce
from cellengine.utils.helpers import timestamp_to_datetime, datetime_to_timestamp


class Folder:
    """A class representing a CellEngine folder."""

    def __init__(self, properties: Dict[str, Any]):
        self._properties = properties
        self._changes = set()

    @property
    def _id(self) -> str:
        return self._properties["_id"]

    @property
    def id(self) -> str:
        """Alias for ``_id``."""
        return self._properties["_id"]

    @property
    def name(self) -> str:
        return self._properties["name"]

    @name.setter
    def name(self, name):
        self._properties["name"] = name
        self._changes.add("name")

    @property
    def created(self) -> datetime:
        """The date on which the folder was created."""
        created = self._properties["created"]
        return timestamp_to_datetime(created)

    @property
    def deleted(self) -> Union[datetime, None]:
        """If the folder is soft-deleted, the date on which it was soft-deleted.
        """
        deleted = self._properties["deleted"]
        return timestamp_to_datetime(deleted) if deleted else None

    @deleted.setter
    def deleted(self, deleted: Union[datetime, None]):
        self._properties["deleted"] = (
            datetime_to_timestamp(deleted) if deleted else None
        )
        self._changes.add("deleted")

    @property
    def creator(self) -> Dict[str, Any]:
        return self._properties["creator"]

    @property
    def path(self) -> List[str]:
        """The list of IDs of parent folders."""
        return self._properties["path"]

    @path.setter
    def path(self, path: List[str]):
        self._properties["path"] = path
        self._changes.add("path")

    @property
    def permissions(self) -> List[Dict[str, Any]]:
        return self._properties["permissions"]

    # TODO set_permissions

    @classmethod
    def get(cls, _id: Optional[str] = None, name: Optional[str] = None) -> Folder:
        """Get a Folder by name or ID. Either `name` or `_id` must be specified.

        Args:
            _id (optional): ID of the folder.
            name (optional): Name of the folder.
        """
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_folder(**kwargs)

    @staticmethod
    def create(name: str, path: Optional[List[str]] = []) -> Folder:
        """Creates a folder.

        Args:
            name (str): Name of the folder
            path (str[], optional): Optional path to create the folder in.
                Defaults to [] (root-level).

        Returns:
            The newly created Folder.
        """
        return ce.APIClient().post_folder({"name": name, "path": path})

    def update(self) -> None:
        """Save changes to this Folder to CellEngine."""
        update_properties = {key: self._properties[key] for key in self._changes}
        res = ce.APIClient().update_folder(self._id, update_properties)
        self._properties = res
        self._changes = set()

    def delete(self) -> None:
        """Marks the folder as deleted.

        Deleted folders are permanently deleted after approximately
        7 days. Until then, deleted folders can be recovered.
        """
        self.deleted = datetime.today()  # won't exactly match server, but close
        ce.APIClient().delete_folder(self._id)

    def undelete(self) -> None:
        """Clears a scheduled deletion."""
        if self.deleted:
            self.deleted = None
            ce.APIClient().update_folder(self._id, {"deleted": self.deleted})
