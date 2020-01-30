import attr

@attr.s(repr=False, slots=True)
class Attachment(object):
    """A class representing a CellEngine attachment.
    Attachments are non-data files that are stored in an experiment.
    """

    def __repr__(self):
        return "Attachment(_id='{0}', name='{1}')".format(self._id, self.name)

    _properties = attr.ib(default={}, repr=False)

    crc32c = GetSet("crc32c", read_only=True)

    experiment_id = GetSet("experimentId", read_only=True)

    filename = GetSet("filename")

    md5 = GetSet("md5", read_only=True)

    size = GetSet("size", read_only=True)

    # API Methods

    # upload

    # list

    # delete

    # update

    # download
