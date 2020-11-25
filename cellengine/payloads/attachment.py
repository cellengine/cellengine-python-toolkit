import attr
from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class _Attachment(object):
    """A class containing CellEngine attachment resource properties.
    Attachments are non-data files that are stored in an experiment.
    """

    def __repr__(self):
        return "Attachment(_id='{}', filename='{}')".format(self._id, self.filename)

    _id = GetSet("_id", read_only=True)

    _properties = attr.ib(default={}, repr=False)

    crc32c = GetSet("crc32c", read_only=True)

    experiment_id = GetSet("experimentId", read_only=True)

    filename = GetSet("filename")

    md5 = GetSet("md5", read_only=True)

    size = GetSet("size", read_only=True)
