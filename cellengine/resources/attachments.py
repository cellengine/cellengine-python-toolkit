import attr
from cellengine.utils.helpers import (
    GetSet,
    base_list,
    session,
    base_delete,
    base_update,
    base_get,
)


@attr.s(repr=False, slots=True)
class Attachment(object):
    """A class representing a CellEngine attachment.
    Attachments are non-data files that are stored in an experiment.
    """

    def __repr__(self):
        return "Attachment(_id='{}', filename='{}')".format(self._id, self.filename)

    _properties = attr.ib(default={}, repr=False)

    _id = GetSet("_id", read_only=True)

    crc32c = GetSet("crc32c", read_only=True)

    experiment_id = GetSet("experimentId", read_only=True)

    filename = GetSet("filename")

    md5 = GetSet("md5", read_only=True)

    size = GetSet("size", read_only=True)

    # API Methods

    @classmethod
    def list(cls, experiment_id):
        url = "experiments/{0}/attachments".format(experiment_id)
        return base_list(url, Attachment)

    # upload

    @classmethod
    def create(cls, experiment_id: str, filepath: str):
        files = {"upload_file": open(filepath, "rb")}
        res = session.post(
            "experiments/{0}/attachments".format(experiment_id), files=files
        )
        if res.ok:
            return cls(res.json())

    def delete(self):
        return base_delete(
            "experiments/{0}/attachments/{1}".format(self.experiment_id, self._id)
        )

    def update(self):
        """Save any changed data to CellEngine."""
        res = base_update(
            "experiments/{0}/attachments/{1}".format(self.experiment_id, self._id),
            body=self._properties,
        )
        self._properties.update(res)

    def download(self, to_file: str = None):
        """Download the attachment.

        Defaults to returning the file. If ``to_file`` is specified, the file
        will be saved to disk.

        Args:
            to_file (str): Filepath at which to save the file. Accepts relative or
                absolute path.

        Returns:
            content: JSON-serializable if possible, otherwise the raw response content.
        """
        res = base_get(
            "experiments/{0}/attachments/{1}".format(self.experiment_id, self._id)
        )
        if to_file:
            with open(to_file, "wb") as f:
                f.write(res)
        else:
            return res
