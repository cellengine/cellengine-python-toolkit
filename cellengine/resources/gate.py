from typing import Dict, List
import attr
from cellengine.utils.helpers import (
    GetSet,
    base_create,
    base_delete,
    base_update,
)
from cellengine.resources import Gates

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
        return "{}(_id='{}', name='{}')".format(self.type, self._id, self.name)

    @classmethod
    def create(cls, gates: Dict) -> List["Gate"]:
        """Build a Gate object from a dict of properties.

        Args:
            experiment_id (str): The ID of the experiment to which to add the gate. Use
                when calling this as a static method; not needed when calling from an
                Experiment object.
            name (str): The name of the gate
            x_channel (str): The name of the x channel to which the gate applies.
            gid (str): Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. If you wish you create
                a tailored gate, you must specify the gid of the global tailored gate.
            parent_population_id (str): ID of the parent population. Use ``None`` for
                the 'ungated' population. If specified, do not specify
                ``parent_population``.
            parent_population (str): Name of the parent population. An attempt will
                be made to find the population by name.  If zero or more than
                one population exists with the name, an error will be thrown.
                If specified, do not specify ``parent_population_id``.
            tailored_per_file (bool): Whether or not this gate is tailored per FCS file.
            fcs_file_id (str): ID of FCS file, if tailored per file. Use ``None`` for
                the global gate in a tailored gate group. If specified, do not
                specify ``fcs_file``.
            fcs_file (str): Name of FCS file, if tailored per file. An attempt will
                be made to find the file by name. If zero or more than one file exists
                with the name, an error will be thrown. Looking up files by name is
                slower than using the ID, as this requires additional requests
                to the server. If specified, do not specify ``fcs_file_id``.
            locked (bool): Prevents modification of the gate via the web interface.
            create_population (bool): Automatically create corresponding population.
            """
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
        except Exception as e:
            raise ValueError("All gates must be posted to the same experiment", e)
        res = cls._post_gate(gates, experiment_id, create_population=False)
        return res

    @classmethod
    def _post_gate(cls, gate, experiment_id, create_population):
        """Post the gate, passing the factory as the class.

        Returns:
            The correct Gate subclass.
        """
        res = base_create(
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

        NOTE: This approach allows users to change the model properties to
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
    def delete_gates(
        experiment_id, _id: str = None, gid: str = None, exclude: str = None
    ):
        """Deletes a gate or a tailored gate family.

        Works for compound gates if you specify the top-level gid. Specifying
        the gid of a sector (i.e. one listed in ``model.gids``) will result in no
        gates being deleted.  If gateId is specified, only that gate will be
        deleted, regardless of the other parameters specified. May be called as
        a static method from cellengine.Gate or from an Experiment instance.

        Args:
            experimentId (str): ID of experiment.
            _id (str): ID of gate family.
            gateId (str): ID of gate.
            exclude (str): Gate ID to exclude from deletion.

        Example:
            ```python
            cellengine.Gate.delete_gate(experiment_id, gid = [gate family ID])
            # or
            experiment.delete_gate(_id = [gate ID])
            ```

        Returns:
            None

        """
        if (_id and gid) or (not _id and not gid):
            raise ValueError("Either the gid or the gateId must be specified")
        if _id:
            url = "experiments/{0}/gates/{1}".format(experiment_id, _id)
        elif gid:
            url = "experiments/{0}/gates?gid={1}".format(experiment_id, gid)
            if exclude:
                url = "{0}%exclude={1}".format(url, exclude)

        base_delete(url)

    # API methods
    def update(self):
        res = base_update(
            "experiments/{0}/gates/{1}".format(self.experiment_id, self._id),
            body=self._properties,
        )
        self._properties.update(res)


class RectangleGate(Gate):
    """Basic concrete class for rectangle gates"""

    @staticmethod
    def create(
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        x1: float,
        x2: float,
        y1: float,
        y2: float,
        label: List[str] = [],
        gid: str = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):
        """Creates a rectangle gate.

        Refer to the [Gate][cellengine.resources.gate.Gate] class for optional args.

        Args:
            x1 (float): The first x coordinate (after the channel's scale has been applied).
            x2 (float): The second x coordinate (after the channel's scale has been applied).
            y1 (float): The first y coordinate (after the channel's scale has been applied).
            y2 (float): The second y coordinate (after the channel's scale has been applied).

        Returns:
            RectangleGate: A RectangleGate object.

        Example:
            ```python
            experiment.create_rectangle_gate(x_channel="FSC-A", y_channel="FSC-W",
            name="my gate", 12.502, 95.102, 1020, 32021.2)
            # or:
            cellengine.Gate.create_rectangle_gate(experiment_id, x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x1=12.5, x2=95.1, y1=1020, y2=32021.2,
            gid=global_gate.gid)
            ```
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
        x_vertices: List[float],
        y_vertices: List[float],
        label: List[float] = [],
        gid: str = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):

        """Creates a polygon gate.

        Refer to the [Gate][cellengine.resources.gate.Gate] class for optional args.

        Args:
            y_channel (str): The name of the y channel to which the gate applies.
            x_vertices (List[float]): List of x coordinates for the polygon's vertices.
            y_vertices (List[float]): List of y coordinates for the polygon's vertices.
            label (List[float]): [x, y] position of the label. Defaults to the midpoint of the gate.

        Returns:
            PolygonGate: A PolygonGate object.

        Example:
            ```python
            experiment.create_polygon_gate(x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x_vertices=[1, 2, 3], y_vertices=[4,
            5, 6])
            ```
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
        x: float,
        y: float,
        angle: float,
        major: float,
        minor: float,
        label: List[float] = [],
        gid: str = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):
        """Creates an ellipse gate.

        Refer to the [Gate][cellengine.resources.gate.Gate] class for optional args.

        Args:
            y_channel (str): The name of the y channel to which the gate applies.
            x (float): The x centerpoint of the gate.
            y (float): The y centerpoint of the gate.
            angle (float): The angle of the ellipse in radians.
            major (float): The major radius of the ellipse.
            minor (float): The minor radius of the ellipse.
            label (List[float]): [x, y] position of the label. Defaults to the midpoint of the gate.

        Returns:
            EllipseGate: An EllipseGate object.

        Example:
            ```python
            cellengine.Gate.create_ellipse_gate(experiment_id, x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x=260000, y=64000, angle=0,
            major=120000, minor=70000)
            ```
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
        x1: float,
        x2: float,
        y: float = 0.5,
        label: List[float] = [],
        gid: str = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):
        """Creates a range gate.

        Refer to the [Gate][cellengine.resources.gate.Gate] class for optional args.

        Args:
            y_channel (str): The name of the y channel to which the gate applies.
            x1 (float): The first x coordinate (after the channel's scale has been applied).
            x2 (float): The second x coordinate (after the channel's scale has been applied).
            y (float): Position of the horizontal line between the vertical lines, in the
            label (List[float]): [x, y] position of the label. Defaults to the midpoint of the gate.

        Returns:
            RangeGate: A RangeGate object.

        Example:
            ```python
            experiment.create_range_gate(x_channel="FSC-A", name="my gate",
            x1=12.502, x2=95.102)
            cellengine.Gate.create_range_gate(experiment_id,
            x_channel="FSC-A", name="my gate",
            12.502, 95.102)
            ```
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
        x: float,
        y: float,
        labels: List[float] = [],
        gid: str = None,
        gids: List[str] = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):
        """
        Creates a quadrant gate. Quadrant gates have four sectors (upper-right,
        upper-left, lower-left, lower-right), each with a unique gid and name.

        Refer to the [Gate][cellengine.resources.gate.Gate] class for optional args.

        Args:
            x (float): The x coordinate of the center point (after the channel's scale has
                been applied).
            y (float): The y coordinate (after the channel's scale has been applied).
            labels (List[float]): Positions of the quadrant labels. A list of four length-2
                lists in the order: UR, UL, LL, LR. These are set automatically to
                the plot corners.
            gids (List[str]): Group IDs of each sector, assigned to ``model.gids``.

        Returns:
            QuadrantGate: A QuadrantGate object.

        Example:
            ```python
            cellengine.Gate.create_quadrant_gate(experimentId, x_channel="FSC-A",
                y_channel="FSC-W", name="my gate", x=160000, y=200000)
            experiment.create_quadrant_gate(x_channel="FSC-A",
                y_channel="FSC-W", name="my gate", x=160000, y=200000,
                labels=[[1, 2] [3, 4], [5, 6], [7, 8]])
            ```
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
        x: float,
        y: float,
        labels: List[float] = [],
        gid: str = None,
        gids: List[str] = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):
        """
        Creates a split gate. Split gates have two sectors (right and left),
        each with a unique gid and name.

        Refer to the [Gate][cellengine.resources.gate.Gate] class for optional args.

        Args:
            x (float): The x coordinate of the center point (after the channel's scale has
                been applied).  y: The y coordinate of the dashed line extending from
                the center point (after the channel's scale has been applied).
            labels (List[float]): Positions of the quadrant labels. A list of two length-2 lists in
                the order: L, R. These are set automatically to the top corners.
            gids (List[str]): Group IDs of each sector, assigned to model.gids.

        Returns:
            SplitGate: A SplitGate object.

        Example:
            ```python
            cellengine.Gate.create_split_gate(experiment_id, x_channel="FSC-A",
            name="my gate", x=144000, y=100000)
            experiment.create_split_gate(x_channel="FSC-A", name="my gate", x=144000,
                y=100000)
            ```
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
