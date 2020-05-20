import attr
from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class _Population(object):
    """
    A class representing a CellEngine population.

    Attributes
        _properties (:obj:`dict`): Population properties; reqired.
    """

    def __repr__(self):
        return "Population(_id='{}', name='{}')".format(self._id, self.name)

    _properties = attr.ib()

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

    experiment_id = GetSet("experimentId", read_only=True)

    gates = GetSet("gates")

    terminal_gate_gid = GetSet("terminalGateId")

    parent_id = GetSet("parentId")

    unique_name = GetSet("uniqueName", read_only=True)
