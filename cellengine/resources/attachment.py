from __future__ import annotations
from typing import Optional, Any, Dict
from datetime import datetime
import cellengine as ce
from cellengine.utils.helpers import timestamp_to_datetime


class Attachment:
    """A class representing a CellEngine attachment.
    Attachments are non-data files that are stored in an experiment.
    """

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
    def experiment_id(self) -> str:
        return self._properties["experimentId"]

    @property
    def filename(self) -> str:
        return self._properties["filename"]

    @filename.setter
    def filename(self, filename):
        self._properties["filename"] = filename
        self._changes.add("filename")

    @property
    def md5(self) -> str:
        return self._properties["md5"]

    @property
    def crc32c(self) -> str:
        return self._properties["crc32c"]

    @property
    def size(self) -> int:
        return self._properties["size"]

    @property
    def created(self) -> datetime:
        created = self._properties["created"]
        return timestamp_to_datetime(created)

    @classmethod
    def get(
        cls, experiment_id: str, _id: Optional[str] = None, name: Optional[str] = None
    ) -> Attachment:
        """Get an Attachment by name or ID for a specific experiment. Either
        `name` or `_id` must be specified.

        Args:
            experiment_id: ID of the experiment this attachment is connected with.
            _id (optional): ID of the attachment.
            name (optional): Name of the experiment.
        """
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_attachment(experiment_id, **kwargs)

    @staticmethod
    def upload(
        experiment_id: str, filepath: str, filename: Optional[str] = None
    ) -> Attachment:
        """Upload an attachment

        Args:
            filepath (str): Local path to file to upload.
            filename (str, optional): Optionally, specify a new name for the file.

        Returns:
            The newly uploaded Attachment.
        """
        return ce.APIClient().upload_attachment(experiment_id, filepath, filename)

    def update(self) -> None:
        """Save changes to this Attachment to CellEngine."""
        update_properties = {key: self._properties[key] for key in self._changes}
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "attachments", update_properties
        )
        self._properties = res
        self._changes = set()

    def download(self, to_file: Optional[str] = None) -> Optional[bytes]:
        """Download the attachment.

        Defaults to returning the file as a blob. If ``to_file`` is specified,
        the file will be saved to disk.

        Args:
            to_file (str): Path at which to save the file. Accepts relative or
                absolute paths.

        Returns:
            content: The raw response content.
        """
        res = ce.APIClient().download_attachment(self.experiment_id, self._id)

        if to_file:
            with open(to_file, "wb") as f:
                f.write(res)
        else:
            return res

    def delete(self) -> None:
        ce.APIClient().delete_entity(self.experiment_id, "attachments", self._id)
