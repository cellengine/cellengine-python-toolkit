import attr
from munch import Munch, munchify

from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class _ScaleSet(object):
    """A class containing CellEngine scaleset resource properties."""

    def __repr__(self):
        return "ScaleSet(_id='{}', name='{}')".format(self._id, self.name)

    _properties = attr.ib()

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

    experiment_id = GetSet("experimentId", read_only=True)

    @property
    def scales(self):
        scales = self._properties["scales"]
        if type(scales) is not Munch:
            self._properties["scales"] = munchify(scales)
        return munchify(scales)
