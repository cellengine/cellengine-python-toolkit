import attr

from cellengine.utils.helpers import GetSet
from cellengine.payloads.scale_utils.scale_dict import ScaleDict


@attr.s(repr=False)
class _ScaleSet(object):
    """A class containing CellEngine scaleset resource properties."""

    def __repr__(self):
        return "ScaleSet(_id='{}', name='{}')".format(self._id, self.name)

    _properties = attr.ib()

    _scales = attr.ib(default=None, repr=False)

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

    experiment_id = GetSet("experimentId", read_only=True)

    @property
    def scales(self):
        if not self._scales:
            self._scales = {
                item["channelName"]: ScaleDict(item["scale"])
                for item in self._properties["scales"]
            }
        return self._scales
