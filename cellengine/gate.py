import attr
import munch
from . import _helpers
from .Gates import (
    create_rectangle_gate,
    create_ellipse_gate,
    create_polygon_gate,
    create_range_gate,
    create_split_gate,
    create_quadrant_gate,
)
from .Gates.gate_util import create_gates


@attr.s(repr=False)
class Gate(object):
    """A class representing a CellEngine gate.

    Gates are geometric shapes that define boundaries within which events
    (cells) must be contained to be considered part of a population.

    Gates may be any one of RectangleGate, PolygonGate, EllipseGate, RangeGate,
    QuadrantGate or SplitGate. See ``help(cellengine.Gate.<Gate Type>)`` for
    specific args.

    When tailoring a gate to a file, a new gate is created with the same GID as
    the original gate, but with an fcs_file_id property set to the file to which
    the gate is tailored. To create a tailored gate, first create a global
    tailored gate by passing ``tailored_per_file=True`` and
    ``fcs_file_id=None`` to a gate creation method. Subsequent tailored gates
    may be created with ``tailored_per_file=True`` and ``gid=<global gate
    gid>``.

    The update and delete API endpoints accept requests by GID to make
    for efficient updates to families of tailored gates.

    Compound gates (quadrant and split) are made up of "sectors." Quadrant
    gates have four sectors (upper-right, upper-left, lower-left, lower-right)
    and split gates have two sectors (left and right). In addition to the
    top-level GID (like simple gates), these gates have model.gids and names
    lists that specify the GID and name for each sector, in the order shown
    above. Populations using compound gates must reference these sector GIDs;
    referencing the top-level GID of a compound gate is meaningless.
    """

    def __repr__(self):
        return "Gate(_id='{0}', name='{1}', type={2})".format(
            self._id, self.name, self.type
        )

    _properties = attr.ib(default={}, repr=False)

    _id = _helpers.GetSet("_id", read_only=True)

    name = _helpers.GetSet("name")

    # TODO: bad usage of a Python builtin; can we change this? (is functional)
    type = _helpers.GetSet("type")

    experiment_id = _helpers.GetSet("experimentId", read_only=True)

    gid = _helpers.GetSet("gid")

    x_channel = _helpers.GetSet("xChannel")

    y_channel = _helpers.GetSet("yChannel")

    tailored_per_file = _helpers.GetSet("tailoredPerFile")

    fcs_file_id = _helpers.GetSet("fcsFileId")

    parent_population_id = _helpers.GetSet("parentPopulationId")

    names = _helpers.GetSet("names")

    @property
    def model(self):
        """Return an attribute-style dict of the model.

        NOTE: This approach does allow users to change the model properties to
        invalid values (i.e. 'rectangle' to a str from a dict). We could
        prevent this by making Gate.model return a __slot__ class "Model", where each
        attr of Model was built dynamically. I wrote it this way at first, but
        couldn't figure out a way to write both get and set attribute-style accessors
        for the class. Munch does this really nicely.

        As it is, this relies on the API to validate the model. If necessary, I
        can write validators in here as well.
        """
        model = self._properties["model"]
        if type(model) is not Gate._Munch:
            self._properties["model"] = munch.munchify(model, factory=self._Munch)
        return model

    @model.setter
    def model(self, val):
        model = self._properties["model"]
        model.update(val)

    class _Munch(munch.Munch):
        """Extend the Munch class for a dict-like __repr__"""

        def __repr__(self):
            return "{0}".format(dict.__repr__(self))

    # gate creation methods

    create_gates = staticmethod(create_gates)

    create_rectangle_gate = staticmethod(create_rectangle_gate)

    create_polygon_gate = staticmethod(create_polygon_gate)

    create_ellipse_gate = staticmethod(create_ellipse_gate)

    create_range_gate = staticmethod(create_range_gate)

    create_split_gate = staticmethod(create_split_gate)

    create_quadrant_gate = staticmethod(create_quadrant_gate)
