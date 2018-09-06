import attr
from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class _Compensation(object):
    """A class containing CellEngine compensation resource properties. Can be applied to
    FCS files to compensate them.
    """

    def __repr__(self):
        return "Compensation(_id='{}', name='{}')".format(self._id, self.name)

    _id = GetSet("_id", read_only=True)

    _properties = attr.ib(default={}, repr=False)

    _dataframe = attr.ib(default=None, repr=False)

    name = GetSet("name")

    experiment_id = GetSet("experimentId", read_only=True)

    channels = GetSet("channels")

    @property
    def N(self):
        return len(self.channels)
