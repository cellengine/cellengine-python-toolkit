import cellengine as ce
from cellengine.payloads.attachment import _Attachment


class Attachment(_Attachment):
    """A class representing a CellEngine attachment.
    Attachments are non-data files that are stored in an experiment.
    """

    @classmethod
    def get(cls, experiment_id: str, _id: str = None, name: str = None):
        """Get an Attachment by name or ID for a specific experiment. Either
        `name` or `id` must be specified.

        Args:
            experiment_id: ID of the experiment this attachment is connected with.
            _id (optional): ID of the attachment.
            name (optional): Name of the experiment.
        """
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_attachment(experiment_id, **kwargs)

    @staticmethod
    def upload(experiment_id: str, filepath: str, filename: str = None):
        return ce.APIClient().post_attachment(experiment_id, filepath, filename)

    def update(self):
        """Save changes to this Attachment to CellEngine.

        Returns:
            None: Updates the Attachment on CellEngine and then
                synchronizes the properties with the current Attachment object.
        """
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "attachments", body=self._properties
        )
        self._properties.update(res)

    def delete(self):
        """Delete this attachment."""
        return ce.APIClient().delete_entity(self.experiment_id, "attachments", self._id)

    def download(self, to_file: str = None):
        """Download the attachment.

        Defaults to returning the file as a blob. If ``to_file`` is specified, the file
        will be saved to disk.

        Args:
            to_file (str): Filepath at which to save the file. Accepts relative or
                absolute path.

        Returns:
            content: The raw response content.
        """
        res = ce.APIClient().download_attachment(self.experiment_id, self._id)

        if to_file:
            with open(to_file, "wb") as f:
                f.write(res)
        else:
            return res
