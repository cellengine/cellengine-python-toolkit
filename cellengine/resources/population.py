cellengine = __import__(__name__.split(".")[0])
import attr
from cellengine.utils import helpers
from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class Population(object):
    """
    A class representing a CellEngine population.

    Attributes
        _properties (:obj:`dict`): Population properties; reqired.
    """

    def __repr__(self):
        return "Population(_id='{0}', name='{1}')".format(self._id, self.name)

    _properties = attr.ib()

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

    experiment_id = GetSet("experimentId", read_only=True)

    gates = GetSet("gates")

    terminal_gate_gid = GetSet("terminalGateId")

    parent_id = GetSet("parentId")

    unique_name = GetSet("uniqueName", read_only=True)

    def update(self):
        """Save any changed data to CellEngine."""
        return helpers.base_update(
            "experiments/{0}/populations/{1}".format(self.experiment_id, self._id),
            body=self._properties,
            classname=Population,
        )


    def delete(self):
        return helpers.base_delete(
            "experiments/{0}/populations/{1}".format(self.experiment_id, self._id)
        )
