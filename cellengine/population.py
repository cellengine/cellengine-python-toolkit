cellengine = __import__(__name__.split(".")[0])
import attr
from .client import session
from . import _helpers


@attr.s(repr=False)
class Population(object):
    """
    A class representing a CellEngine population.

    Attributes
        _properties (:obj:`dict`): Population properties; reqired.
    """

    def __repr__(self):
        return "Population(_id='{0}', name='{1}')".format(self._id, self.name)

    _properties = attr.ib()

    _id = _helpers.GetSet("_id", read_only=True)

    name = _helpers.GetSet("name")

    experiment_id = _helpers.GetSet("experimentId", read_only=True)

    gates = _helpers.GetSet("gates")

    terminal_gate_gid = _helpers.GetSet("terminalGateId")

    parent_id = _helpers.GetSet("parentId")

    unique_name = _helpers.GetSet("uniqueName", read_only=True)

    def update(self):
        """Save any changed data to CellEngine."""
        return _helpers.base_update(
            "experiments/{0}/populations/{1}".format(self.experiment_id, self._id),
            body=self._properties,
            classname=Population,
        )

    # delete
    def delete(self):
        return _helpers.base_delete(
            "experiments/{0}/populations/{1}".format(self.experiment_id, self._id)
        )
