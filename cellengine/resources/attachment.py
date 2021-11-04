from __future__ import annotations
from attr import define, field

import cellengine as ce
from cellengine.utils import readonly, converter


@define
class Attachment:
    """A class representing a CellEngine attachment.
    Attachments are non-data files that are stored in an experiment.
    """

    _id: str = field(on_setattr=readonly)
    filename: str
    crc32c: str = field(on_setattr=readonly, repr=False)
    experiment_id: str = field(on_setattr=readonly, repr=False)
    md5: str = field(on_setattr=readonly, repr=False)
    size: int = field(on_setattr=readonly, repr=False)

    @property
    def client(self):
        return ce.APIClient()

    def update(self):
        """Save changes to this Attachment to CellEngine."""
        res = self.client.update(self)
        self.__setstate__(res.__getstate__())  # type: ignore

    @classmethod
    def from_dict(cls, data: dict):
        return converter.structure(data, cls)

    def to_dict(self):
        return converter.unstructure(self)

    def asdict(self):
        """Force use of cattrs"""
        return self.to_dict()

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

    def delete(self):
        return self.client.delete_entity(self.experiment_id, "attachments", self._id)
