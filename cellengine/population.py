cellengine = __import__(__name__.split(".")[0])
import attr
from . import helpers


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

    _id = helpers.GetSet("_id", read_only=True)

    name = helpers.GetSet("name")

    experiment_id = helpers.GetSet("experimentId", read_only=True)

    gates = helpers.GetSet("gates")

    terminal_gate_gid = helpers.GetSet("terminalGateId")

    parent_id = helpers.GetSet("parentId")

    unique_name = helpers.GetSet("uniqueName", read_only=True)

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
