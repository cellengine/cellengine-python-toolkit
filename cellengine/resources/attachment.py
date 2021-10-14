from __future__ import annotations
from dataclasses import dataclass, field
from dataclasses_json.cfg import config

import cellengine as ce
from cellengine.utils.dataclass_mixin import DataClassMixin, ReadOnly


@dataclass
class Attachment(DataClassMixin):
    """A class representing a CellEngine attachment.
    Attachments are non-data files that are stored in an experiment.
    """

    filename: str
    _id: str = field(
        metadata=config(field_name="_id"), default=ReadOnly()
    )  # type: ignore
    crc32c: str = field(repr=False, default=ReadOnly())  # type: ignore
    experiment_id: str = field(repr=False, default=ReadOnly())  # type: ignore
    md5: str = field(repr=False, default=ReadOnly())  # type: ignore
    size: int = field(repr=False, default=ReadOnly())  # type: ignore

    @classmethod
    def get(cls, experiment_id: str, _id: str = None, name: str = None) -> Attachment:
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
    def upload(experiment_id: str, filepath: str, filename: str = None) -> Attachment:
        return ce.APIClient().post_attachment(experiment_id, filepath, filename)

    def update(self):
        """Save changes to this Attachment to CellEngine.

        Returns:
            None: Updates the Attachment on CellEngine and synchronizes the
                local Attachment object properties with remote state.
        """
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "attachments", body=self.to_dict()
        )
        self.__dict__.update(Attachment.from_dict(res).__dict__)

    def delete(self):
        """Delete this attachment."""
        return ce.APIClient().delete_entity(self.experiment_id, "attachments", self._id)

    def download(self, to_file: str = None):
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
