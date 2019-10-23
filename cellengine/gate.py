import attr
import numpy
from cellengine import helpers
from .helpers import convert_dict
from . import Gates
from custom_inherit import doc_inherit

import importlib
from abc import ABC
import munch
from . import _helpers
from .Gates import (create_rectangle_gate, create_ellipse_gate,
                    create_polygon_gate, create_range_gate, create_split_gate,
                    create_quadrant_gate)
from .Gates.gate_util import create_gates


@attr.s(repr=False, slots=True)
class Gate(ABC):
    """
    Args: (In all gate types, refer to help for each gate for args specific to
        that gate.)

        experiment_id: The ID of the experiment to which to add the
        gate.
            Use when calling this as a static method; not needed when calling
            from an Experiment object
        name: The name of the gate
        x_channel: The name of the x channel to which the gate applies.
        gid: Group ID of the gate, used for tailoring. If this is not
            specified, then a new Group ID will be created. If you wish you
            create a tailored gate, you must specify the gid of the global
            tailored gate.
        parent_population_id: ID of the parent population. Use ``None`` for
            the "ungated" population. If specified, do not specify
            ``parent_population``.
        parent_population: Name of the parent population. An attempt will
            be made to find the population by name.  If zero or more than
            one population exists with the name, an error will be thrown.
            If specified, do not specify ``parent_population_id``.
        tailored_per_file: Whether or not this gate is tailored per FCS file.
        fcs_file_id: ID of FCS file, if tailored per file. Use ``None`` for
            the global gate in a tailored gate group. If specified, do not
            specify ``fcs_file``.
        fcs_file: Name of FCS file, if tailored per file. An attempt will be made
            to find the file by name. If zero or more than one file exists with
            the name, an error will be thrown. Looking up files by name is
            slower than using the ID, as this requires additional requests
            to the server. If specified, do not specify ``fcs_file_id``.
        locked: Prevents modification of the gate via the web interface.
        create_population: Automatically create corresponding population.
    """

    _posted = attr.ib(default=False)

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
    _properties = attr.ib(default={}, repr=False)

    def __repr__(self):
        return "Gate(_id=\'{0}\', name=\'{1}\', type={2})".format(self._id, self.name, self.type)

    _id = _helpers.GetSet('_id', read_only=True)

    @classmethod
    def _post_gate(cls, gate, experiment_id, create_population):
        """Post the gate, passing the factory as the class, which returns the correct subclass."""
        res = helpers.base_create(
            "experiments/{}/gates".format(experiment_id),
            json=gate,
            expected_status=201,
            params={"createPopulation": create_population},
            classname=Gate,
        )
        return res

    # TODO: bad usage of a Python builtin; can we change this? (is functional)
    type = _helpers.GetSet('type')

    _id = helpers.GetSet("_id", read_only=True)

    name = helpers.GetSet("name")

    type = helpers.GetSet("type", read_only=True)

    experiment_id = helpers.GetSet("experimentId", read_only=True)

    gid = helpers.GetSet("gid")

    x_channel = helpers.GetSet("xChannel")

    y_channel = helpers.GetSet("yChannel")

    tailored_per_file = helpers.GetSet("tailoredPerFile")

    fcs_file_id = helpers.GetSet("fcsFileId")

    parent_population_id = helpers.GetSet("parentPopulationId")

    names = helpers.GetSet("names")

    # TODO: create_population()

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
        model = self._properties['model']
        if type(model) is not Gate._Munch:
            self._properties['model'] = munch.munchify(model, factory=self._Munch)
        return model

    @model.setter
    def model(self, val):
        model = self._properties['model']
        model.update(val)

    class _Munch(munch.Munch):
        """Extend the Munch class for a dict-like __repr__"""
        def __repr__(self):
            return '{0}'.format(dict.__repr__(self))

    def delete_gates(experiment_id, _id=None, gid=None, exclude=None):
        """
        Deletes a gate or a tailored gate family.

        Works for compound gates if you specify the top-level gid. Specifying
        the gid of a sector (i.e. one listed in model.gids) will result in no
        gates being deleted.  If gateId is specified, only that gate will be
        deleted, regardless of the other parameters specified. May be called as
        a static method from cellengine.Gate or from an Experiment instance.

        Args:
            experimentId: ID of experiment.
            _id: ID of gate family.
            gateId: ID of gate.
            exclude: Gate ID to exclude from deletion.

        Examples:
            cellengine.Gate.delete_gate(experiment_id, gid = [gate family ID])
            experiment.delete_gate(_id = [gate ID])

        """
        if (_id and gid) or (not _id and not gid):
            raise ValueError("Either the gid or the gateId must be specified")
        if _id:
            url = "experiments/{0}/gates/{1}".format(experiment_id, _id)
        elif gid:
            url = "experiments/{0}/gates?gid={1}".format(experiment_id, gid)
            if exclude:
                url = "{0}%exclude={1}".format(url, exclude)

        helpers.base_delete(url)


class RectangleGate(Gate):
    """Basic concrete class for polygon gates"""

    @staticmethod
    def create(
        experiment_id,
        x_channel,
        y_channel,
        name,
        x1,
        x2,
        y1,
        y2,
        label=[],
        gid=None,
        locked=False,
        parent_population_id=None,
        parent_population=None,
        tailored_per_file=False,
        fcs_file_id=None,
        fcs_file=None,
        create_population=True,
    ):
        """Creates a rectangle gate.

        Required Args: ``(refer to help(cellengine.Gate)`` for optional args.
            x1: The first x coordinate (after the channel's scale has been applied).
            x2: The second x coordinate (after the channel's scale has been applied).
            y1: The first y coordinate (after the channel's scale has been applied).
            y2: The second y coordinate (after the channel's scale has been applied).

        Returns:
            A RectangleGate object.

        Example:
            experiment.create_rectangle_gate(x_channel="FSC-A", y_channel="FSC-W",
            name="my gate", 12.502, 95.102, 1020, 32021.2)
            cellengine.Gate.create_rectangle_gate(experiment_id, x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x1=12.502, x2=95.102, y1=1020, y2=32021.2,
            gid=global_gate.gid)
        """

        formatted_gate = Gates.create_rectangle_gate(
            experiment_id,
            x_channel,
            y_channel,
            name,
            x1,
            x2,
            y1,
            y2,
            label,
            gid,
            locked,
            parent_population_id,
            parent_population,
            tailored_per_file,
            fcs_file_id,
            fcs_file,
            create_population,
        )
        return Gate.create(formatted_gate)

    create_polygon_gate = staticmethod(create_polygon_gate)

    create_ellipse_gate = staticmethod(create_ellipse_gate)

    @staticmethod
    def create(
        experiment_id,
        x_channel,
        y_channel,
        name,
        x_vertices,
        y_vertices,
        label=[],
        gid=None,
        locked=False,
        parent_population_id=None,
        parent_population=None,
        tailored_per_file=False,
        fcs_file_id=None,
        fcs_file=None,
        create_population=True,
    ):

        """Creates a polygon gate.

        Required Args: ``(refer to help(cellengine.Gate)`` for optional args.
            y_channel: The name of the y channel to which the gate applies.
            x_vertices: List of x coordinates for the polygon's vertices.
            y_vertices List of y coordinates for the polygon's vertices.
            label: Position of the label. Defaults to the midpoint of the gate.

        Returns:
            A PolygonGate object.

        Example:
            experiment.create_polygon_gate(x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x_vertices=[1, 2, 3], y_vertices=[4,
            5, 6])
        """
        formatted_gate = Gates.create_polygon_gate(
            experiment_id,
            x_channel,
            y_channel,
            name,
            x_vertices,
            y_vertices,
            label,
            gid,
            locked,
            parent_population_id,
            parent_population,
            tailored_per_file,
            fcs_file_id,
            fcs_file,
            create_population,
        )
        return Gate.create(formatted_gate)

    create_split_gate = staticmethod(create_split_gate)

    create_quadrant_gate = staticmethod(create_quadrant_gate)

    @staticmethod
    def create(
        experiment_id,
        x_channel,
        y_channel,
        name,
        x,
        y,
        angle,
        major,
        minor,
        label=[],
        gid=None,
        locked=False,
        parent_population_id=None,
        parent_population=None,
        tailored_per_file=False,
        fcs_file_id=None,
        fcs_file=None,
        create_population=True,
    ):
        """Creates an ellipse gate.

        Required Args: ``(refer to help(cellengine.Gate)`` for optional args.
            y_channel: The name of the y channel to which the gate applies.
            x: The x centerpoint of the gate.
            y: The y centerpoint of the gate.
            angle: The angle of the ellipse in radians.
            major: The major radius of the ellipse.
            minor: The minor radius of the ellipse.
            label: Position of the label. Defaults to the midpoint of the gate.

        Returns:
            An EllipseGate object.

        Example:
            cellengine.Gate.create_ellipse_gate(experiment_id, x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x=260000, y=64000, angle=0,
            major=120000, minor=70000)
        """
        formatted_gate = Gates.create_ellipse_gate(
            experiment_id,
            x_channel,
            y_channel,
            name,
            x,
            y,
            angle,
            major,
            minor,
            label,
            gid,
            locked,
            parent_population_id,
            parent_population,
            tailored_per_file,
            fcs_file_id,
            fcs_file,
            create_population,
        )
        return Gate.create(formatted_gate)


class RangeGate(Gate):
    """Basic concrete class for range gates"""

    def create(
        experiment_id,
        x_channel,
        name,
        x1,
        x2,
        y=0.5,
        label=[],
        gid=None,
        locked=False,
        parent_population_id=None,
        parent_population=None,
        tailored_per_file=False,
        fcs_file_id=None,
        fcs_file=None,
        create_population=True,
    ):
        """Creates a range gate.

        Required Args: ``(refer to help(cellengine.Gate)`` for optional args.
            y_channel: The name of the y channel to which the gate applies.
            x1: The first x coordinate (after the channel's scale has been applied).
            x2: The second x coordinate (after the channel's scale has been applied).
            y: Position of the horizontal line between the vertical lines, in the
            label: Position of the label. Defaults to the midpoint of the gate.

        Returns:
            A RangeGate object.

        Example:
            experiment.create_range_gate(x_channel="FSC-A", name="my gate",
            x1=12.502, x2=95.102)
            cellengine.Gate.create_range_gate(experiment_id,
            x_channel="FSC-A", name="my gate",
            12.502, 95.102)
            """
        formatted_gate = Gates.create_range_gate(
            experiment_id,
            x_channel,
            name,
            x1,
            x2,
            y,
            label,
            gid,
            locked,
            parent_population_id,
            parent_population,
            tailored_per_file,
            fcs_file_id,
            fcs_file,
            create_population,
        )
        return Gate.create(formatted_gate)


class QuadrantGate(Gate):
    """Basic concrete class for quadrant gates"""

    def create(
        experiment_id,
        x_channel,
        y_channel,
        name,
        x,
        y,
        labels=[],
        gid=None,
        gids=None,
        locked=False,
        parent_population_id=None,
        parent_population=None,
        tailored_per_file=False,
        fcs_file_id=None,
        fcs_file=None,
        create_population=True,
    ):
        """
        Creates a quadrant gate. Quadrant gates have four sectors (upper-right,
        upper-left, lower-left, lower-right), each with a unique gid and name.

        Required Args: ``(refer to help(cellengine.Gate)`` for optional args.
            x: The x coordinate of the center point (after the channel's scale has
                been applied).
            y: The y coordinate (after the channel's scale has been applied).
            labels: Positions of the quadrant labels. A list of four length-2
                vectors in the order: UR, UL, LL, LR. These are set automatically to
                the plot corners.
            gids: Group IDs of each sector, assigned to ``model.gids``.

        Returns:
            A QuadrantGate object.

        Example:
            cellengine.Gate.create_quadrant_gate(experimentId, x_channel="FSC-A",
                y_channel="FSC-W", name="my gate", x=160000, y=200000)
            experiment.create_quadrant_gate(x_channel="FSC-A",
                y_channel="FSC-W", name="my gate", x=160000, y=200000)
        """
        formatted_gate = Gates.create_quadrant_gate(
            experiment_id,
            x_channel,
            y_channel,
            name,
            x,
            y,
            labels,
            gid,
            gids,
            locked,
            parent_population_id,
            parent_population,
            tailored_per_file,
            fcs_file_id,
            fcs_file,
            create_population,
        )
        return Gate.create(formatted_gate)


class SplitGate(Gate):
    """Basic concrete class for split gates"""

    def create(
        experiment_id,
        x_channel,
        name,
        x,
        y,
        labels=[],
        gid=None,
        gids=None,
        locked=False,
        parent_population_id=None,
        parent_population=None,
        tailored_per_file=False,
        fcs_file_id=None,
        fcs_file=None,
        create_population=True,
    ):
        """
        Creates a split gate. Split gates have two sectors (right and left),
        each with a unique gid and name.

        Required Args: ``(refer to help(cellengine.Gate)`` for optional args.
            x: The x coordinate of the center point (after the channel's scale has
                been applied).  y: The y coordinate of the dashed line extending from
                the center point (after the channel's scale has been applied).
            labels: Positions of the quadrant labels. A list of two length-2 lists in
                the order: L, R. These are set automatically to the top corners.
            gids: Group IDs of each sector, assigned to model.gids.

        Returns:
            A SplitGate object.

        Example:
            cellengine.Gate.create_split_gate(experiment_id, x_channel="FSC-A",
            name="my gate", x=144000, y=100000)
            experiment.create_split_gate(x_channel="FSC-A", name="my gate", x=144000,
                y=100000)
            """
        formatted_gate = Gates.create_split_gate(
            experiment_id,
            x_channel,
            name,
            x,
            y,
            labels,
            gid,
            gids,
            locked,
            parent_population_id,
            parent_population,
            tailored_per_file,
            fcs_file_id,
            fcs_file,
            create_population,
        )
        return Gate.create(formatted_gate)
