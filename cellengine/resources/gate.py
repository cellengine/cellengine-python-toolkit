from typing import Dict, List
import attr
import numpy
from cellengine.utils import helpers
from cellengine.utils.helpers import GetSet, convert_dict
from cellengine.utils.helpers import convert_dict
from cellengine.resources import Gates
from custom_inherit import doc_inherit

import importlib
from abc import ABC
import munch


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

    _population = attr.ib(default=None)

    _properties = attr.ib(default={})

    def __repr__(self):
        return "{}(_id={}, name={})".format(self.type, self._id, self.name)

    @classmethod
    def create(cls, gates: Dict) -> List['Gate']:
        """Build a Gate object from a dict of properties."""
        if type(gates) is list:
            return cls._create_multiple_gates(gates)
        else:
            return cls._create_gate(gates)

    @classmethod
    def _create_gate(cls, gate):
        """Get the gate type and return instance of the correct subclass."""
        module = importlib.import_module(__name__)
        gate_type = getattr(module, gate["type"])
        return gate_type(properties=gate)

    @classmethod
    def _create_multiple_gates(cls, gates: list):
        """Create an array of gates.
        Cellengine does not accept createPopulation when an array of gates is created
        """
        experiment_id = gates[0]["experimentId"]
        try:
            assert all([gate["experimentId"] == experiment_id for gate in gates])
        except ValueError:
            print("All gates must be posted to the same experiment")
        res = cls._post_gate(gates, experiment_id, create_population=False)
        return res

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

    def post(self):
        """Post a gate and update properties."""
        res = self._post_gate(
            self._properties, experiment_id=self.experiment_id, create_population=True
        )
        self._posted = True
        self._properties = res._properties

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

    type = GetSet("type", read_only=True)

    experiment_id = GetSet("experimentId", read_only=True)

    gid = GetSet("gid")

    x_channel = GetSet("xChannel")

    y_channel = GetSet("yChannel")

    tailored_per_file = GetSet("tailoredPerFile")

    fcs_file_id = GetSet("fcsFileId")

    parent_population_id = GetSet("parentPopulationId")

    names = GetSet("names")

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

        As it is, this relies on the API to validate the model
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

    @staticmethod
    def delete_gates(experiment_id, _id=None, gid=None, exclude: bool = None):
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

    # API methods
    def update(self):
        res = helpers.base_update("experiments/{0}/gates/{1}".format(self.experiment_id, self._id), body = self._properties)
        self._properties.update(res)


class RectangleGate(Gate):
    """Basic concrete class for polygon gates"""

    @staticmethod
    def create(
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        x1: int,
        x2: int,
        y1: int,
        y2: int,
        label: List[str] = [],
        gid: str = None,
        locked: bool =False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):
        """Creates a rectangle gate.

        Required Args: (refer to ``help(cellengine.Gate``) for optional args.
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


class PolygonGate(Gate):
    """Basic concrete class for polygon gates"""

    @staticmethod
    def create(
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        x_vertices: int,
        y_vertices: int,
        label: List[str] = [],
        gid: str = None,
        locked: bool =False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True
    ):

        """Creates a polygon gate.

        Required Args: (refer to ``help(cellengine.Gate``) for optional args.
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


class EllipseGate(Gate):
    """Basic concrete class for ellipse gates"""

    @staticmethod
    def create(
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        x: int,
        y: int,
        angle: int,
        major: int,
        minor: int,
        label: List[str] = [],
        gid: str = None,
        locked: bool =False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True
    ):
        """Creates an ellipse gate.

        Required Args: (refer to ``help(cellengine.Gate``) for optional args.
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
        experiment_id: str,
        x_channel: str,
        name: str,
        x1: int,
        x2: int,
        y: int = 0.5,
        label: List[str] = [],
        gid: str = None,
        locked: bool =False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True
    ):
        """Creates a range gate.

        Required Args: (refer to ``help(cellengine.Gate``) for optional args.
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
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        x: int,
        y: int,
        labels: List[str] = [],
        gid: str = None,
        gids: List[str] = None,
        locked: bool =False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True
    ):
        """
        Creates a quadrant gate. Quadrant gates have four sectors (upper-right,
        upper-left, lower-left, lower-right), each with a unique gid and name.

        Required Args: (refer to ``help(cellengine.Gate``) for optional args.
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
        experiment_id: str,
        x_channel: str,
        name: str,
        x: int,
        y: int,
        labels: List[str] = [],
        gid: str = None,
        gids: List[str] = None,
        locked: bool =False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True
    ):
        """
        Creates a split gate. Split gates have two sectors (right and left),
        each with a unique gid and name.

        Required Args: (refer to ``help(cellengine.Gate``) for optional args.
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
