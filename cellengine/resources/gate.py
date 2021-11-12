from __future__ import annotations
from typing import Dict, List, Optional
from math import pi

from attr import define, field
import numpy

import cellengine as ce
from cellengine.utils import parse_fcs_file_args
from cellengine.resources.fcs_file import FcsFile
from cellengine.utils import converter, readonly, generate_id


@define(repr=False)
class Gate:
    _id: str = field(on_setattr=readonly)
    experiment_id: str = field(on_setattr=readonly)
    fcs_file_id: Optional[str]
    gid: Optional[str]
    parent_population_id: Optional[str]
    tailored_per_file: Optional[bool]
    type: str
    x_channel: str
    model: Dict
    names: Optional[List[str]] = field(default=None)
    name: Optional[str] = field(default=None)
    y_channel: Optional[str] = field(default=None)

    def __repr__(self):
        if self.name:
            label, name = ("name", self.name)
        else:
            label, name = ("names", str(self.names))
        return f"{self.type}(_id='{self._id}', {label}='{name}')"

    @property
    def client(self):
        return ce.APIClient()

    @property
    def path(self):
        return f"experiments/{self.experiment_id}/gates/{self._id}".rstrip("/None")

    def update(self):
        """Save changes to this Gate to CellEngine.
        If this gate does not exist, it will be created."""
        if not self._id or not is_good_id(self._id):
            gate = self.client.create(self)
        else:
            gate = self.client.update(self)
        self.__setstate__(gate.__getstate__())  # type: ignore

    @classmethod
    def factory(cls, gate):
        """Create a gate from a dict of keys."""
        if "_id" not in gate.keys():
            gate["_id"] = None
        return converter.structure(gate, Gate)

    def delete(self):
        self.client.delete_gate(self.experiment_id, self._id)

    @staticmethod
    def update_family(experiment_id, gid: str, body: Dict):
        """Update a given field for a gate family.

        Warning: This method does not modify local versions of gates; use the
        `.update()` method to ensure changes are reflected locally.

        Args:
            experiment_id: ID of experiment
            gid: ID of gate family to modify
            body (dict): camelCase properties to update

        Returns:
            Raises a warning if no gates are modified, else None
        """

        res = ce.APIClient().update_gate_family(experiment_id, gid, body)
        if res["nModified"] < 1:
            raise Warning("No gates updated.")

    def tailor_to(self, fcs_file: FcsFile):
        self.tailored_per_file = True
        self.fcs_file_id = fcs_file._id
        self.update()


@define(repr=False)
class RectangleGate(Gate):
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        x1: float,
        x2: float,
        y1: float,
        y2: float,
        label: List[float] = [],
        gid: str = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,  # TODO
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):
        """Formats a rectangle gate for posting to the CellEngine API.

        Args:
            experiment_id (str): The ID of the experiment.
            x_channel (float): The name of the x channel to which the gate applies.
            y_channel (float): The name of the y channel to which the gate applies.
            name (str): The name of the gate x1 (float): The first x coordinate
                (after the channel's scale has been applied).
            x2 (float): The second x coordinate (after the channel's scale
                has been applied).
            y1 (float): The first y coordinate (after the channel's scale has
                been applied).
            y2 (float): The second y coordinate (after the channel's scale has
                been applied).
            label (float): Position of the label. Defaults to the midpoint of the gate.
            gid (str): Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be specified.
            locked (bool): Prevents modification of the gate via the web interface.
            parent_population_id (str): ID of the parent population. Use ``None`` for
                the "ungated" population. If specified, do not specify
                ``parent_population``.
            parent_population (str): Name of the parent population. An attempt will
                be made to find the population by name.  If zero or more than
                one population exists with the name, an error will be thrown.
                If specified, do not specify ``parent_population_id``.
            tailored_per_file (bool): Whether or not this gate is tailored per FCS file.
            fcs_file_id (str): ID of FCS file, if tailored per file. Use ``None`` for
                the global gate in a tailored gate group. If specified, do not
                specify ``fcs_file``.
            fcs_file (str): Name of FCS file, if tailored per file. An attempt
                will be made to find the file by name. If zero or more than one file
                exists with the name, an error will be thrown. Looking up files
                by name is slower than using the ID, as this requires
                additional requests to the server. If specified, do not specify
                ``fcs_file_id``.
            create_population (bool): Automatically create corresponding population.

        Returns:
            A RectangleGate object.

        Example:
            ```python
            experiment.create_rectangle_gate(x_channel="FSC-A", y_channel="FSC-W",
            name="my gate", 12.502, 95.102, 1020, 32021.2)
            cellengine.Gate.create_rectangle_gate(experiment_id, x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x1=12.502, x2=95.102, y1=1020,
            y2=32021.2, gid=global_gate.gid)
            ```
        """

        fcs_file_id = parse_fcs_file_args(
            experiment_id, tailored_per_file, fcs_file_id, fcs_file,
        )

        if label == []:
            label = [numpy.mean([x1, x2]), numpy.mean([y1, y2])]
        if not gid:
            gid = generate_id()

        model = {
            "locked": locked,
            "label": label,
            "rectangle": {"x1": x1, "x2": x2, "y1": y1, "y2": y2},
        }

        return Gate(
            id=None,
            experiment_id=experiment_id,
            fcs_file_id=fcs_file_id,
            gid=gid,
            parent_population_id=parent_population_id,
            tailored_per_file=tailored_per_file,
            type="RectangleGate",
            x_channel=x_channel,
            model=model,
            y_channel=y_channel,
            name=name,
            # TODO: create_population
        )  # type: ignore


@define(repr=False)
class PolygonGate(Gate):
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        vertices: List[List[float]],
        label: Optional[List[float]] = [],
        gid: Optional[str] = None,
        locked: Optional[bool] = False,
        parent_population_id: Optional[str] = None,
        parent_population: Optional[str] = None,
        tailored_per_file: Optional[bool] = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Optional[bool] = True,
    ) -> PolygonGate:
        """Formats a polygon gate for posting to the CellEngine API.

        Args:
            experiment_id (str): The ID of the experiment.
            x_channel (str): The name of the x channel to which the gate applies.
            y_channel (str): The name of the y channel to which the gate applies.
            vertices (list): List of coordinates, like [[x,y], [x,y], ...]
            label (str): Position of the label. Defaults to the midpoint of the gate.
            name (str): The name of the gate
            gid (str): Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be specified.
            locked (bool): Prevents modification of the gate via the web interface.
            parent_population_id (str): ID of the parent population. Use ``None`` for
                the "ungated" population. If specified, do not specify
                ``parent_population``.
            parent_population (str): Name of the parent population. An attempt will
                be made to find the population by name.  If zero or more than
                one population exists with the name, an error will be thrown.
                If specified, do not specify ``parent_population_id``.
            tailored_per_file (bool): Whether or not this gate is tailored per FCS file.
            fcs_file_id (str): ID of FCS file, if tailored per file. Use ``None`` for
                the global gate in a tailored gate group. If specified, do not
                specify ``fcs_file``.
            fcs_file (str): Name of FCS file, if tailored per file. An attempt
                will be made to find the file by name. If zero or more than one
                file exists with the name, an error will be thrown. Looking up
                files by name is slower than using the ID, as this requires
                additional requests to the server. If specified, do not specify
                ``fcs_file_id``.
            create_population (bool): Automatically create corresponding population.

        Returns:
            A PolygonGate object.

        Example:
            ```python
            experiment.create_polygon_gate(x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", vertices=[[1,4], [2,5], [3,6]])
            ```
        """

        fcs_file_id = parse_fcs_file_args(
            experiment_id, tailored_per_file, fcs_file_id, fcs_file,
        )

        if label == []:
            label = [
                numpy.mean([item[0] for item in vertices]),
                numpy.mean([item[1] for item in vertices]),
            ]
        if not gid:
            gid = generate_id()

        model = {
            "locked": locked,
            "label": label,
            "polygon": {"vertices": vertices},
        }

        return Gate(
            id=None,
            experiment_id=experiment_id,
            fcs_file_id=fcs_file_id,
            gid=gid,
            parent_population_id=parent_population_id,
            tailored_per_file=tailored_per_file,
            type="PolygonGate",
            x_channel=x_channel,
            model=model,
            y_channel=y_channel,
            name=name,
            # TODO: create_population
        )  # type: ignore


@define(repr=False)
class EllipseGate(Gate):
    @classmethod
    def create(
        cls,
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
    ) -> EllipseGate:
        """Formats an ellipse gate for posting to the CellEngine API.

        Args:
            experiment_id (str): The ID of the experiment.
            x_channel (str): The name of the x channel to which the gate applies.
            y_channel (str): The name of the y channel to which the gate applies.
            name (str): The name of the gate
            x (float): The x centerpoint of the gate.
            y (float): The y centerpoint of the gate.
            angle (float): The angle of the ellipse in radians.
            major (float): The major radius of the ellipse.
            minor (float): The minor radius of the ellipse.
            label (float, optional): Position of the label. Defaults to the
                midpoint of the gate.
            gid (str, optional): Group ID of the gate, used for tailoring. If this
                is not specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be
                specified.
            locked (bool, optional): Prevents modification of the gate via the web
                interface.
            parent_population_id (Optional[str]): ID of the parent population. Use
                ``None`` for the "ungated" population. If specified, do not specify
                ``parent_population``.
            parent_population (str, optional): Name of the parent population. An
                attempt will be made to find the population by name.  If zero or
                more than one population exists with the name, an error will be
                thrown. If specified, do not specify ``parent_population_id``.
            tailored_per_file (bool, optional): Whether or not this gate is
                tailored per FCS file.  fcs_file_id (str, optional): ID of FCS
                file, if tailored per file. Use ``None`` for the global gate in a
                tailored gate group. If specified, do not specify ``fcs_file``.
            fcs_file (str, optional): Name of FCS file, if tailored per file. An
                attempt will be made to find the file by name. If zero or more than
                one file exists with the name, an error will be thrown. Looking up
                files by name is slower than using the ID, as this requires
                additional requests to the server. If specified, do not specify
                ``fcs_file_id``.
            create_population (optional, bool): Automatically create corresponding
                population.

        Returns:
            EllipseGate: An EllipseGate object.

        Examples:
            ```python
            cellengine.Gate.create_ellipse_gate(experiment_id, x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x=260000, y=64000, angle=0,
            major=120000, minor=70000)
            ```
        """

        fcs_file_id = parse_fcs_file_args(
            experiment_id, tailored_per_file, fcs_file_id, fcs_file,
        )

        if label == []:
            label = [x, y]
        if not gid:
            gid = generate_id()

        model = {
            "locked": locked,
            "label": label,
            "ellipse": {
                "angle": angle,
                "major": major,
                "minor": minor,
                "center": [x, y],
            },
        }

        return Gate(
            id=None,
            experiment_id=experiment_id,
            fcs_file_id=fcs_file_id,
            gid=gid,
            parent_population_id=parent_population_id,
            tailored_per_file=tailored_per_file,
            type="EllipseGate",
            x_channel=x_channel,
            model=model,
            y_channel=y_channel,
            name=name,
            # TODO: create_population
        )  # type: ignore


@define(repr=False)
class RangeGate(Gate):
    @classmethod
    def create(
        cls,
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
    ) -> RangeGate:
        """Formats a range gate for posting to the CellEngine API.

        Args:
            experiment_id (str): The ID of the experiment.
            x_channel (str): The name of the x channel to which the gate applies.
            name (str): The name of the gate
            x1 (float): The first x coordinate (after the channel's scale has
                been applied).
            x2 (float): The second x coordinate (after the channel's scale has been
                applied).
            y (float): Position of the horizontal line between the vertical lines
            label (float): Position of the label. Defaults to the midpoint of the gate.
            gid (str): Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be specified.
            locked (bool): Prevents modification of the gate via the web interface.
            parent_population_id (str): ID of the parent population. Use ``None`` for
                the "ungated" population. If specified, do not specify
                ``parent_population``.
            parent_population (str): Name of the parent population. An attempt will
                be made to find the population by name.  If zero or more than
                one population exists with the name, an error will be thrown.
                If specified, do not specify ``parent_population_id``.
            tailored_per_file (bool): Whether or not this gate is tailored per FCS file.
            fcs_file_id (str): ID of FCS file, if tailored per file. Use ``None`` for
                the global gate in a tailored gate group. If specified, do not
                specify ``fcs_file``.
            fcs_file (str): Name of FCS file, if tailored per file. An attempt
                will be made to find the file by name. If zero or more than one
                file exists with the name, an error will be thrown. Looking up
                files by name is slower than using the ID, as this requires
                additional requests to the server. If specified, do not specify
                ``fcs_file_id``.
            create_population (bool): Automatically create corresponding population.

        Returns:
            A RangeGate object.

        Example:
            ```python
            experiment.create_range_gate(x_channel="FSC-A", name="my gate",
            x1=12.502, x2=95.102)
            cellengine.Gate.create_range_gate(experiment_id,
            x_channel="FSC-A", name="my gate",
            12.502, 95.102)
            ```
        """
        fcs_file_id = parse_fcs_file_args(
            experiment_id, tailored_per_file, fcs_file_id, fcs_file,
        )

        if label == []:
            label = [numpy.mean([x1, x2]), y]
        if not gid:
            gid = generate_id()

        model = {
            "locked": locked,
            "label": label,
            "range": {"x1": x1, "x2": x2, "y": y},
        }

        return Gate(
            id=None,
            experiment_id=experiment_id,
            fcs_file_id=fcs_file_id,
            gid=gid,
            parent_population_id=parent_population_id,
            tailored_per_file=tailored_per_file,
            type="RangeGate",
            x_channel=x_channel,
            model=model,
            y_channel=None,
            name=name,
            # TODO: create_population
        )  # type: ignore


@define(repr=False)
class QuadrantGate(Gate):
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        x: float,
        y: float,
        labels: List[List[float]] = [],
        skewable: bool = False,
        angles: List[float] = [0, pi / 2, pi, 3 * pi / 2],
        gid: str = None,
        gids: List[str] = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ) -> QuadrantGate:
        """Formats a quadrant gate for posting to the CellEngine API.

        Quadrant gates have four sectors (upper-right, upper-left, lower-left,
        lower-right), each with a unique gid and name.

        Args:
            experiment_id (str): The ID of the experiment.
            x_channel (str): The name of the x channel to which the gate applies.
            y_channel (str): The name of the y channel to which the gate applies.
            name (str): The name of the gate
            x (float): The x coordinate of the center point (after the
                channel's scale has been applied).
            y (float): The y coordinate (after the channel's scale has been applied).
            labels (list): Positions of the quadrant labels. A list of four length-2
                vectors in the order: UR, UL, LL, LR. These are set automatically to
                the plot corners.
            skewable (bool): Whether the quadrant gate is skewable.
            angles (list): List of the four angles of the quadrant demarcations
            gid (str): Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be specified.
            gids (list): Group IDs of each sector, assigned to ``model.gids``.
            locked (bool): Prevents modification of the gate via the web interface.
            parent_population_id (str): ID of the parent population. Use ``None`` for
                the "ungated" population. If specified, do not specify
                ``parent_population``.
            parent_population (str): Name of the parent population. An attempt will
                be made to find the population by name.  If zero or more than
                one population exists with the name, an error will be thrown.
                If specified, do not specify ``parent_population_id``.
            tailored_per_file (bool): Whether or not this gate is tailored per FCS file.
            fcs_file_id (str): ID of FCS file, if tailored per file. Use ``None`` for
                the global gate in a tailored gate group. If specified, do not
                specify ``fcs_file``.
            fcs_file (str): Name of FCS file, if tailored per file. An attempt
                will be made to find the file by name. If zero or more than one
                file exists with the name, an error will be thrown. Looking up
                files by name is slower than using the ID, as this requires
                additional requests to the server. If specified, do not specify
                ``fcs_file_id``.
            create_population (bool): Automatically create corresponding population.

        Returns:
            A QuadrantGate object.

        Example:
            ```python
            cellengine.Gate.create_quadrant_gate(experimentId, x_channel="FSC-A",
                y_channel="FSC-W", name="my gate", x=160000, y=200000)
            experiment.create_quadrant_gate(x_channel="FSC-A",
                y_channel="FSC-W", name="my gate", x=160000, y=200000)
            ```
        """

        fcs_file_id = parse_fcs_file_args(
            experiment_id, tailored_per_file, fcs_file_id, fcs_file,
        )

        # set labels based on axis scale
        r = ce.APIClient().get_scaleset(experiment_id, as_dict=True)
        scale_min = min(x["scale"]["minimum"] for x in r["scales"])
        scale_max = max(x["scale"]["minimum"] for x in r["scales"])

        if labels == []:
            labels = [
                [scale_max, scale_max],  # upper right
                [scale_min, scale_max],  # upper left
                [scale_min, scale_min],  # lower left
                [scale_max, scale_min],  # lower right
            ]  # lower right

        elif len(labels) == 4 and all(len(label) == 2 for label in labels):
            pass
        else:
            raise ValueError("Labels must be a list of four length-2 lists.")

        if not gid:
            gid = generate_id()
        if gids is None:
            gids = [
                generate_id(),
                generate_id(),
                generate_id(),
                generate_id(),
            ]

        names = [name + append for append in [" (UR)", " (UL)", " (LL)", " (LR)"]]

        model = {
            "locked": locked,
            "labels": labels,
            "gids": gids,
            "skewable": skewable,
            "quadrant": {"x": x, "y": y, "angles": angles},
        }

        return Gate(
            id=None,
            experiment_id=experiment_id,
            fcs_file_id=fcs_file_id,
            gid=gid,
            parent_population_id=parent_population_id,
            tailored_per_file=tailored_per_file,
            type="QuadrantGate",
            x_channel=x_channel,
            model=model,
            y_channel=y_channel,
            names=names,
            # TODO: create_population
        )  # type: ignore


@define(repr=False)
class SplitGate(Gate):
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        name: str,
        x: float,
        y: float = 0.5,
        labels: List[List[float]] = [],
        gid: str = None,
        gids: List[str] = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ) -> SplitGate:
        """
        Formats a split gate for posting to the CellEngine API.

        Split gates have two sectors (right and left),
        each with a unique gid and name.

        Args:
            experiment_id (str): The ID of the experiment.
            x_channel (str): The name of the x channel to which the gate applies.
            name (str): The name of the gate.
            x (float): The x coordinate of the center point (after the
                channel's scale has been applied).
            y (float): The relative position from 0 to 1 of the dashed line extending
                from the center point.
            labels (list): Positions of the quadrant labels. A list of two
                length-2 lists in the order: L, R. These are set automatically
                to the top corners.
            gid (str): Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be specified.
            gids (list): Group IDs of each sector, assigned to model.gids.
            locked (bool): Prevents modification of the gate via the web interface.
            parent_population_id (str): ID of the parent population. Use ``None`` for
                the "ungated" population. If specified, do not specify
                ``parent_population``.
            parent_population (str): Name of the parent population. An attempt will
                be made to find the population by name.  If zero or more than
                one population exists with the name, an error will be thrown.
                If specified, do not specify ``parent_population_id``.
            tailored_per_file (bool): Whether or not this gate is tailored per FCS file.
            fcs_file_id (str): ID of FCS file, if tailored per file. Use ``None`` for
                the global gate in a tailored gate group. If specified, do not
                specify ``fcs_file``.
            fcs_file (str): Name of FCS file, if tailored per file. An attempt
                will be made to find the file by name. If zero or more than one
                file exists with the name, an error will be thrown. Looking up
                files by name is slower than using the ID, as this requires
                additional requests to the server. If specified, do not specify
                ``fcs_file_id``.
            create_population (bool): Automatically create corresponding population.

        Returns:
            A SplitGate object.

        Example:
            ```python
            cellengine.Gate.create_split_gate(experiment_id, x_channel="FSC-A",
            name="my gate", x=144000, y=100000)
            experiment.create_split_gate(x_channel="FSC-A", name="my gate", x=144000,
                y=100000)
            ```
        """

        fcs_file_id = parse_fcs_file_args(
            experiment_id, tailored_per_file, fcs_file_id, fcs_file,
        )

        # set labels based on axis scale
        r = ce.APIClient().get_scaleset(experiment_id, as_dict=True)
        scale_min = min(x["scale"]["minimum"] for x in r["scales"])
        scale_max = max(x["scale"]["minimum"] for x in r["scales"])

        if labels == []:
            labels = [
                [scale_min + 0.1 * scale_max, 0.916],
                [scale_max - 0.1 * scale_max, 0.916],
            ]
        elif len(labels) == 2 and len(labels[0]) == 2 and len(labels[1]) == 2:
            pass
        else:
            raise ValueError("Labels must be a list of two length-2 lists.")

        if not gid:
            gid = generate_id()
            if gids is None:
                gids = [generate_id(), generate_id()]

        names = [name + " (L)", name + " (R)"]

        model = {
            "locked": locked,
            "labels": labels,
            "gids": gids,
            "split": {"x": x, "y": y},
        }

        return Gate(
            id=None,
            experiment_id=experiment_id,
            fcs_file_id=fcs_file_id,
            gid=gid,
            parent_population_id=parent_population_id,
            tailored_per_file=tailored_per_file,
            type="SplitGate",
            x_channel=x_channel,
            model=model,
            y_channel=None,
            names=names,
            # TODO: create_population
        )  # type: ignore
