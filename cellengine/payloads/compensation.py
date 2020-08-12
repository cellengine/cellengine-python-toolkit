import attr
import pandas
import numpy
from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class _Compensation(object):
    """A class representing a CellEngine compensation matrix. Can be applied to
    FCS files to compensate them.
    """

    def __repr__(self):
        return "Compensation(_id='{}', name='{}')".format(self._id, self.name)

    _properties = attr.ib(default={}, repr=False)

    _dataframe = attr.ib(default=None, repr=False)

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

    experiment_id = GetSet("experimentId", read_only=True)

    channels = GetSet("channels")

    @property
    def N(self):
        return len(self.channels)
