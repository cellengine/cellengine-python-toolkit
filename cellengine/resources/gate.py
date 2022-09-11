from __future__ import annotations
import importlib
from math import pi
from operator import itemgetter
from typing import Any, Dict, List, Optional, Union, Tuple, overload

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from attr import define, field
from numpy import array, mean, stack

import cellengine as ce
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.population import Population
from cellengine.utils import parse_fcs_file_args
from cellengine.utils import converter, generate_id, readonly
from cellengine.utils.helpers import (
    get_args_as_kwargs,
    normalize,
    remove_keys_with_none_values,
)

import sys

if sys.version_info[:2] >= (3, 8):
    from collections.abc import Mapping
else:
    from collections import Mapping  # type: ignore


def exception_handler(func):
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            if type(err) is ValueError:
                raise err
            raise RuntimeError(f"Incorrect arguments passed to {func.__name__}.")

    return inner_function


def deep_update(source, overrides):
    """
    Update a nested dictionary or similar mapping.
    Modify `source` in place.
    """
    for key, value in overrides.items():
        if isinstance(value, Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source


@define(repr=False)
class Gate:
    _id: str = field(on_setattr=readonly)
    experiment_id: str = field(on_setattr=readonly)
    gid: str = field(on_setattr=readonly)
    type: str
    x_channel: str
    model: Dict
    tailored_per_file: bool = False
    fcs_file_id: Optional[str] = None
    names: Optional[List[str]] = field(default=None)
    name: Optional[str] = field(default=None)
    y_channel: Optional[str] = field(default=None)

    def __repr__(self):
        if self.name:
            label, name = ("name", self.name)
        else:
            label, name = ("names", str(self.names))
        return f"{self.type}(_id='{self._id}', {label}='{name}')"

    @staticmethod
    def _format_gate(gate, **kwargs):
        module = importlib.import_module("cellengine")
        _class = getattr(module, gate["type"])
        return _class._format(**gate)

    @classmethod
    def create_many(
        cls,
        gates: List[Dict],
    ):
        experiment_id = set([g["experiment_id"] for g in gates])
        if len(experiment_id) != 1:
            raise RuntimeError("Created gates must all be in the same Experiment.")

        formatted_gates = [cls._format_gate(gate) for gate in gates]
        return ce.APIClient().create(
            [Gate(id=None, **g) for g in formatted_gates],  # type: ignore
            create_population=False,
        )

    @property
    def path(self):
        return f"experiments/{self.experiment_id}/gates/{self._id}".rstrip("/None")

    @classmethod
    def from_dict(cls, data: dict):
        return converter.structure(data, cls)

    def to_dict(self):
        return converter.unstructure(self)

    def update(self):
        """Save changes to this Gate to CellEngine."""
        res = ce.APIClient().update(self)
        self.__setstate__(res.__getstate__())  # type: ignore

    def delete(self):
        ce.APIClient().delete_gate(self.experiment_id, self._id)

    @staticmethod
    def update_gate_family(experiment_id: str, gid: str, body: Dict) -> None:
        """Update a given field for a gate family.

        Warning: This method does not modify local versions of gates; use the
        `.update()` method to ensure changes are reflected locally.

        Args:
            experiment_id: ID of experiment
            gid: ID of gate family to modify
            body: camelCase properties to update

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


class RectangleGate(Gate):
    @overload
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
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[True] = True,
        parent_population_id: Optional[str] = None,
    ) -> Tuple[RectangleGate, Population]:
        ...

    @overload
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
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[False] = False,
    ) -> RectangleGate:
        ...

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
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: bool = True,
        parent_population_id: Optional[str] = None,
    ) -> Union[RectangleGate, Tuple[RectangleGate, Population]]:
        """Creates a rectangle gate.

        Args:
            experiment_id: The ID of the experiment.
            x_channel: The name of the x channel to which the gate applies.
            y_channel: The name of the y channel to which the gate applies.
            name: The name of the gate
            x1: The first x coordinate (after the channel's scale has been
                applied).
            x2: The second x coordinate (after the channel's scale has been
                applied).
            y1: The first y coordinate (after the channel's scale has been
                applied).
            y2: The second y coordinate (after the channel's scale has been
                applied).
            label: Position of the label. Defaults to the midpoint of the gate.
            gid: Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. Must be
                specified when creating a tailored gate.
            locked: Prevents modification of the gate via the web interface.
            tailored_per_file: Whether or not this gate is tailored per FCS
                file.
            fcs_file_id: ID of FCS file, if tailored per file. Use `None` for
                the global gate in a tailored gate group. If specified, do not
                specify `fcs_file`.
            fcs_file: Name of FCS file, if tailored per file. An attempt will be
                made to find the file by name. If zero or more than one file
                exists with the name, an error will be thrown. Looking up files
                by name is slower than using the ID, as this requires additional
                requests to the server. If specified, do not specify
                `fcs_file_id`.
            create_population: If true, a corresponding population will be
                created and returned in a tuple with the gate.
            parent_population_id: Use with `create_population` to specify the
                population below which to create this population.

        Returns:
            A RectangleGate if `create_population` is False, or a Tuple with the
                gate and populations if `create_population` is True.

        Examples:
            ```python
            gate, pop = experiment.create_rectangle_gate(
                x_channel="FSC-A",
                y_channel="FSC-W",
                name="my gate",
                x1=12.502,
                x2=95.102,
                y1=1020,
                y2=32021.2)
            ```
        """
        kwargs = get_args_as_kwargs(cls, locals())
        params = {
            k: kwargs.pop(k) for k in ["create_population", "parent_population_id"]
        }

        gate = cls._format(**kwargs)
        return ce.APIClient().create(Gate(id=None, **gate), **params)  # type: ignore

    @classmethod
    @exception_handler
    def _format(cls, **kwargs: Dict[str, Any]):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        x1 = args.get("x1") or args.get("model", {}).get("rectangle", {}).get("x1")
        x2 = args.get("x2") or args.get("model", {}).get("rectangle", {}).get("x2")
        y1 = args.get("y1") or args.get("model", {}).get("rectangle", {}).get("y1")
        y2 = args.get("y2") or args.get("model", {}).get("rectangle", {}).get("y2")
        if not x1 or not x2 or not y1 or not y2:
            raise ValueError("x1, x2, y1 and y2 must be provided.")
        label = args.get("label") or args.get("model", {}).get(
            "label",
            [
                mean([x1, x2]),
                mean([y1, y2]),
            ],
        )

        model = {
            "locked": args.get("locked") or args.get("model", {}).get("locked", False),
            "label": label,
            "rectangle": {"x1": x1, "x2": x2, "y1": y1, "y2": y2},
        }

        return {
            "experiment_id": args["experiment_id"],
            "fcs_file_id": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", generate_id()),
            "model": model,
            "name": args.get("name"),
            "tailored_per_file": args.get("tailored_per_file", False),
            "type": "RectangleGate",
            "x_channel": args.get("x_channel"),
            "y_channel": args.get("y_channel"),
        }


class PolygonGate(Gate):
    @overload
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        vertices: List[List[float]],
        label: List[float] = [],
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[True] = True,
        parent_population_id: Optional[str] = None,  # TODO Ungated
    ) -> Tuple[PolygonGate, Population]:
        ...

    @overload
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        vertices: List[List[float]],
        label: List[float] = [],
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[False] = False,
    ) -> PolygonGate:
        ...

    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        vertices: List[List[float]],
        label: List[float] = [],
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: bool = True,
        parent_population_id: Optional[str] = None,
    ) -> Union[PolygonGate, Tuple[PolygonGate, Population]]:
        """Creates a polygon gate.

        Args:
            experiment_id: The ID of the experiment.
            x_channel: The name of the x channel to which the gate applies.
            y_channel: The name of the y channel to which the gate applies.
            name: The name of the gate
            vertices: List of coordinates, like `[[x,y], [x,y], ...]`.
            label: Position of the label. Defaults to the midpoint of the gate.
            gid: Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be
                specified.
            locked: Prevents modification of the gate via the web interface.
            tailored_per_file: Whether or not this gate is tailored per FCS
                file.
            fcs_file_id: ID of FCS file, if tailored per file. Use `None` for
                the global gate in a tailored gate group. If specified, do not
                specify `fcs_file`.
            fcs_file: Name of FCS file, if tailored per file. An attempt will be
                made to find the file by name. If zero or more than one file
                exists with the name, an error will be thrown. Looking up files
                by name is slower than using the ID, as this requires additional
                requests to the server. If specified, do not specify
                `fcs_file_id`.
            create_population: If true, a corresponding population will be
                created and returned in a tuple with the gate.
            parent_population_id: Use with `create_population` to specify the
                population below which to create this populations.

        Returns:
            A PolygonGate if `create_population` is False, or a Tuple with the
                gate and populations if `create_population` is True.

        Examples:
            ```python
            gate, pop = experiment.create_polygon_gate(
                x_channel="FSC-A",
                y_channel="FSC-W",
                name="my gate",
                vertices=[[1,4], [2,5], [3,6]])
            ```
        """
        kwargs = get_args_as_kwargs(cls, locals())
        params = {
            k: kwargs.pop(k) for k in ["create_population", "parent_population_id"]
        }

        gate = cls._format(**kwargs)
        return ce.APIClient().create(Gate(id=None, **gate), **params)  # type: ignore

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        vertices = args.get("vertices", []) or args.get("model", {}).get(
            "polygon", {}
        ).get("vertices", [])
        label = args.get("label") or args.get("model", {}).get(
            "label", mean(vertices, axis=0).tolist()
        )

        model = {
            "locked": args.get("model", {}).get("locked", False),
            "label": label,
            "polygon": {"vertices": vertices},
        }

        return {
            "experiment_id": args["experiment_id"],
            "fcs_file_id": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", generate_id()),
            "model": model,
            "name": args.get("name"),
            "tailored_per_file": args.get("tailored_per_file", False),
            "type": "PolygonGate",
            "x_channel": args.get("x_channel"),
            "y_channel": args.get("y_channel"),
        }


class EllipseGate(Gate):
    @overload
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        center: List[float],
        angle: float,
        major: float,
        minor: float,
        label: List[float] = [],
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[True] = True,
        parent_population_id: Optional[str] = None,  # TODO Ungated
    ) -> Tuple[EllipseGate, Population]:
        ...

    @overload
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        center: List[float],
        angle: float,
        major: float,
        minor: float,
        label: List[float] = [],
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[False] = False,
    ) -> EllipseGate:
        ...

    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        center: List[float],
        angle: float,
        major: float,
        minor: float,
        label: List[float] = [],
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: bool = True,
        parent_population_id: Optional[str] = None,
    ) -> Union[EllipseGate, Tuple[EllipseGate, Population]]:
        """Creates an ellipse gate.

        Args:
            experiment_id: The ID of the experiment.
            x_channel: The name of the x channel to which the gate applies.
            y_channel: The name of the y channel to which the gate applies.
            name: The name of the gate
            center: The x, y centerpoint of the gate.
            angle: The angle of the ellipse in radians.
            major: The major radius of the ellipse.
            minor: The minor radius of the ellipse.
            label: Position of the label. Defaults to the midpoint of the gate.
            gid: Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be
                specified.
            locked: Prevents modification of the gate via the
                web interface.
            tailored_per_file: Whether or not this gate is tailored per FCS
                file.
            fcs_file_id: ID of FCS file, if tailored per file. Use `None` for
                the global gate in a tailored gate group. If specified, do not
                specify `fcs_file`.
            fcs_file: Name of FCS file, if tailored per file. An attempt will be
                made to find the file by name. If zero or more than one file
                exists with the name, an error will be thrown. Looking up files
                by name is slower than using the ID, as this requires additional
                requests to the server. If specified, do not specify
                `fcs_file_id`.
            create_population: If true, a corresponding population will be
                created and returned in a tuple with the gate.
            parent_population_id: Use with `create_population` to specify the
                population below which to create this populations.

        Returns:
            If `create_population` is `True`, a tuple containing an EllipseGate
                and a list of two Populations; otherwise, an EllipseGate.

        Examples:
            ```python
            gate, pop = experiment.create_ellipse_gate(
                x_channel="FSC-A",
                y_channel="FSC-W",
                name="my gate",
                x=260000,
                y=64000,
                angle=0,
                major=120000,
                minor=70000)
            ```
        """
        kwargs = get_args_as_kwargs(cls, locals())
        params = {
            k: kwargs.pop(k) for k in ["create_population", "parent_population_id"]
        }

        gate = cls._format(**kwargs)
        return ce.APIClient().create(Gate(id=None, **gate), **params)  # type: ignore

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        angle = args.get("angle") or args.get("model", {}).get("ellipse", {}).get(
            "angle"
        )
        major = args.get("major") or args.get("model", {}).get("ellipse", {}).get(
            "major"
        )
        minor = args.get("minor") or args.get("model", {}).get("ellipse", {}).get(
            "minor"
        )
        x = args.get("x")
        y = args.get("y")
        if x and y:
            center = [x, y]
        else:
            center = args.get("center") or args.get("model", {}).get("ellipse", {}).get(
                "center"
            )
            x, y = center  # type: ignore

        label = args.get("label") or args.get("model", {}).get("label", [x, y])

        model = {
            "locked": args.get("model", {}).get("locked", False),
            "label": label,
            "ellipse": {
                "angle": angle,
                "major": major,
                "minor": minor,
                "center": center,
            },
        }

        return {
            "experiment_id": args["experiment_id"],
            "fcs_file_id": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", generate_id()),
            "model": model,
            "name": args.get("name"),
            "tailored_per_file": args.get("tailored_per_file", False),
            "type": "EllipseGate",
            "x_channel": args.get("x_channel"),
            "y_channel": args.get("y_channel"),
        }


class RangeGate(Gate):
    @overload
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
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[True] = True,
        parent_population_id: Optional[str] = None,
    ) -> Tuple[RangeGate, Population]:
        ...

    @overload
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
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[False] = False,
    ) -> RangeGate:
        ...

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
        gid: Optional[str] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: bool = True,
        parent_population_id: Optional[str] = None,
    ) -> Union[RangeGate, Tuple[RangeGate, Population]]:
        """Creates a range gate.

        Args:
            experiment_id: The ID of the experiment.
            x_channel: The name of the x channel to which the gate applies.
            name: The name of the gate
            x1: The first x coordinate (after the channel's scale has
                been applied).
            x2: The second x coordinate (after the channel's scale has been
                applied).
            y: Position of the horizontal line between the
                vertical lines
            label: Position of the label. Defaults to
                the midpoint of the gate.
            gid: Group ID of the gate, used for tailoring. If
                this is not specified, then a new Group ID will be created. To
                create a tailored gate, the gid of the global tailored gate
                must be specified.
            locked: Prevents modification of the gate via the
                web interface.
            tailored_per_file: Whether or not this gate is
                tailored per FCS file.
            fcs_file_id: ID of FCS
                file, if tailored per file. Use `None` for the global gate in
                a tailored gate group. If specified, do not specify
                `fcs_file`.
            fcs_file: Name of FCS file, if tailored per file.
                An attempt will be made to find the file by name. If zero or
                more than one file exists with the name, an error will be
                thrown. Looking up files by name is slower than using the ID,
                as this requires additional requests to the server. If
                specified, do not specify `fcs_file_id`.
            create_population: If true, a corresponding population will be
                created and returned in a tuple with the gate.
            parent_population_id: Use with `create_population` to specify the
                population below which to create this populations.

        Returns:
            If `create_population` is `True`, a tuple containing a RangeGate
                and a list of two Populations; otherwise, a RangeGate.

        Examples:
            ```python
            gate, pop = experiment.create_range_gate(
                x_channel="FSC-A",
                name="my gate",
                x1=12.502,
                x2=95.102)
            ```
        """
        kwargs = get_args_as_kwargs(cls, locals())
        params = {
            k: kwargs.pop(k) for k in ["create_population", "parent_population_id"]
        }

        gate = cls._format(**kwargs)
        return ce.APIClient().create(Gate(id=None, **gate), **params)  # type: ignore

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        x1 = args.get("x1") or args.get("model", {}).get("range", {}).get("x1")
        x2 = args.get("x2") or args.get("model", {}).get("range", {}).get("x2")
        y = args.get("y") or args.get("model", {}).get("range", {}).get("y", 0.5)
        if not x1 or not x2:
            raise ValueError("x1 and x2 must be provided.")

        label = args.get("label") or args.get("model", {}).get(
            "label", [mean([x1, x2]), y]
        )

        model = {
            "locked": args.get("model", {}).get("locked", False),
            "label": label,
            "range": {"x1": x1, "x2": x2, "y": y},
        }

        return {
            "experiment_id": args["experiment_id"],
            "fcs_file_id": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", generate_id()),
            "model": model,
            "name": args.get("name"),
            "tailored_per_file": args.get("tailored_per_file", False),
            "type": "RangeGate",
            "x_channel": args.get("x_channel"),
        }


class QuadrantGate(Gate):
    @overload
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
        gid: Optional[str] = None,
        gids: Optional[List[str]] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[True] = True,
        parent_population_id: Optional[str] = None,  # TODO Ungated
    ) -> Tuple[QuadrantGate, List[Population]]:
        ...

    @overload
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
        gid: Optional[str] = None,
        gids: Optional[List[str]] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[False] = False,
    ) -> QuadrantGate:
        ...

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
        gid: Optional[str] = None,
        gids: Optional[List[str]] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: bool = True,
        parent_population_id: Optional[str] = None,
    ) -> Union[QuadrantGate, Tuple[QuadrantGate, List[Population]]]:
        """Creates a quadrant gate.

        Quadrant gates have four sectors (upper-right, upper-left, lower-left,
        lower-right), each with a unique gid and name.

        Args:
            experiment_id: The ID of the experiment.
            x_channel: The name of the x channel to which the gate applies.
            y_channel: The name of the y channel to which the gate applies.
            name: The name of the gate
            x: The x coordinate of the center point (after the channel's scale
                has been applied).
            y: The y coordinate (after the channel's scale has been applied).
            labels: Positions of the quadrant labels. A list of four length-2
                vectors in the order UR, UL, LL, LR. These are set automatically
                to the plot corners.
            skewable: Whether the quadrant gate is skewable.
            angles: List of the four angles of the quadrant demarcations
            gid: Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be
                specified.
            gids: Group IDs of each sector, assigned to `model.gids`.
            locked: Prevents modification of the gate via the web
                interface.
            tailored_per_file: Whether or not this gate is
                tailored per FCS file.
            fcs_file_id: ID of FCS file, if tailored per file.
                Use `None` for the global gate in a tailored gate group. If
                specified, do not specify `fcs_file`.
            fcs_file: Name of FCS file, if tailored per file.
                An attempt will be made to find the file by name. If zero or
                more than one file exists with the name, an error will be
                thrown. Looking up files by name is slower than using the ID,
                as this requires additional requests to the server. If
                specified, do not specify `fcs_file_id`.
            create_population: If true, corresponding populations will be
                created and returned in a tuple with the gate.
            parent_population_id: Use with `create_population` to specify the
                population below which to create these populations.

        Returns:
            If `create_population` is `True`, a tuple containing the
                QuadrantGate and a list of two Populations; otherwise, a
                QuadrantGate.

        Examples:
            ```python
            gate, pops = experiment.create_quadrant_gate(
                x_channel="FSC-A",
                y_channel="FSC-W",
                name="my gate",
                x=160000,
                y=200000)
            ```
        """
        kwargs = get_args_as_kwargs(cls, locals())
        params = {
            k: kwargs.pop(k) for k in ["create_population", "parent_population_id"]
        }

        gate = cls._format(**kwargs)
        return ce.APIClient().create(Gate(id=None, **gate), **params)  # type: ignore

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        x = args.get("x") or args.get("model", {}).get("quadrant", {}).get("x")
        y = args.get("y") or args.get("model", {}).get("quadrant", {}).get("y")
        angles = (
            args.get("model", {})
            .get("quadrant", {})
            .get("angles", [0, pi / 2, pi, 3 * pi / 2])
        )
        labels = args.get("labels") or args.get("model", {}).get("labels", [])

        if labels == []:
            labels = cls._nudge_labels(
                labels,
                args["experiment_id"],
                args["x_channel"],
                args["y_channel"],
            )
        if not (len(labels) == 4 and all(len(label) == 2 for label in labels)):
            raise ValueError("Labels must be a list of four length-2 lists.")

        model = {
            "locked": args.get("gids") or args.get("model", {}).get("locked", False),
            "labels": labels,
            "gids": args.get("gids")
            or args.get("model", {}).get(
                "gids", [generate_id(), generate_id(), generate_id(), generate_id()]
            ),
            "skewable": args.get("model", {}).get("skewable", False),
            "quadrant": {
                "x": x,
                "y": y,
                "angles": angles,
            },
        }

        default_gid = generate_id()
        return {
            "experiment_id": args["experiment_id"],
            "fcs_file_id": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", default_gid),
            "model": model,
            "names": args.get(
                "names",
                [
                    args.get("name", default_gid) + suffix
                    for suffix in [" (UR)", " (UL)", " (LL)", " (LR)"]
                ],
            ),
            "tailored_per_file": args.get("tailored_per_file", False),
            "type": "QuadrantGate",
            "x_channel": args.get("x_channel"),
            "y_channel": args.get("y_channel"),
        }

    @classmethod
    def _nudge_labels(
        cls, labels: List, experiment_id: str, x_channel: str, y_channel: str
    ) -> List:
        # set labels based on axis scale
        scaleset = ce.APIClient().get_scaleset(experiment_id)
        xmin, xmax = itemgetter("minimum", "maximum")(scaleset.scales[x_channel])
        ymin, ymax = itemgetter("minimum", "maximum")(scaleset.scales[y_channel])

        # nudge labels in from plot corners by pixels
        nudged_labels = array([[290, 290], [0, 290], [0, 0], [290, 0]]) + array(
            [[-32, -16], [40, -16], [40, 15], [-32, 15]]
        )

        # scale the nudged px labels to the actual x and y ranges
        x_scale = normalize(nudged_labels[:, 0], 0, 290, xmin, xmax)
        y_scale = normalize(nudged_labels[:, 1], 0, 290, ymin, ymax)

        labels = stack((x_scale, y_scale)).T.astype(int).tolist()
        return labels


class SplitGate(Gate):
    @overload
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        name: str,
        x: float,
        y: float,
        labels: List[List[float]] = [],
        gid: Optional[str] = None,
        gids: Optional[List[str]] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[True] = True,
        parent_population_id: Optional[str] = None,  # TODO Ungated
    ) -> Tuple[SplitGate, List[Population]]:
        ...

    @overload
    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        name: str,
        x: float,
        y: float,
        labels: List[List[float]] = [],
        gid: Optional[str] = None,
        gids: Optional[List[str]] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: Literal[False] = False,
    ) -> SplitGate:
        ...

    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        name: str,
        x: float,
        y: float = 0.5,
        labels: List[List[float]] = [],
        gid: Optional[str] = None,
        gids: Optional[List[str]] = None,
        locked: bool = False,
        tailored_per_file: bool = False,
        fcs_file_id: Optional[str] = None,
        fcs_file: Optional[str] = None,
        create_population: bool = True,
        parent_population_id: Optional[str] = None,
    ) -> Union[SplitGate, Tuple[SplitGate, List[Population]]]:
        """
        Creates a split gate.

        Split gates have two sectors (right and left), each with a unique gid
        and name.

        Args:
            experiment_id: The ID of the experiment.
            x_channel: The name of the x channel to which the gate applies.
            name: The name of the gate.
            x: The x coordinate of the center point (after the
                channel's scale has been applied).
            y: The relative position from 0 to 1 of the horizontal dashed line
                extending from the center point.
            labels: Positions of the quadrant labels. A list of two length-2
                lists in the order: L, R. These are set automatically to the top
                corners.
            gid: Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. To create a
                tailored gate, the gid of the global tailored gate must be
                specified.
            gids: Group IDs of each sector, assigned to `model.gids`.
            locked: Prevents modification of the gate via the web interface.
            tailored_per_file: Whether or not this gate is tailored per FCS
                file.
            fcs_file_id: ID of FCS file, if tailored per file. Use `None` for
                the global gate in a tailored gate group. If specified, do not
                specify `fcs_file`.
            fcs_file: Name of FCS file, if tailored per file. An attempt will
                be made to find the file by name. If zero or more than one file
                exists with the name, an error will be thrown. Looking up files
                by name is slower than using the ID, as this requires additional
                requests to the server. If specified, do not specify
                `fcs_file_id`.
            create_population: If true, corresponding populations will be
                created and returned in a tuple with the gate.
            parent_population_id: Use with `create_population` to specify the
                population below which to create these populations.

        Returns:
            A SplitGate if `create_population` is False, or a Tuple with the
                gate and populations if `create_population` is True.

        Examples:
            ```python
            # With automatic creation of the corresponding populations:
            gate, pops = experiment.create_split_gate(
                experiment_id,
                x_channel="FSC-A",
                name="my gate",
                x=144000, y=0.5,
                parent_population_id="...")
            # Without
            gate = experiment.create_split_gate(
                experiment_id,
                x_channel="FSC-A",
                name="my gate",
                x=144000, y=0.5,
                create_population=False)
            ```
        """
        kwargs = get_args_as_kwargs(cls, locals())
        params = {
            k: kwargs.pop(k) for k in ["create_population", "parent_population_id"]
        }

        gate = cls._format(**kwargs)
        return ce.APIClient().create(Gate(id=None, **gate), **params)  # type: ignore

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        x = args.get("x") or args.get("model", {}).get("split", {}).get("x")
        y = args.get("y") or args.get("model", {}).get("split", {}).get("y", 0.5)

        labels = args.get("labels") or args.get("model", {}).get("labels", [])

        labels = args.get("labels") or args.get("model", {}).get("labels", [])

        if labels == []:
            labels = cls._generate_labels(
                labels, args["experiment_id"], args["x_channel"]
            )
        if not len(labels) == 2 and len(labels[0]) == 2 and len(labels[1]) == 2:
            raise ValueError("Labels must be a list of two length-2 lists.")

        model = {
            "locked": args.get("locked") or args.get("model", {}).get("locked", False),
            "labels": labels,
            "gids": args.get("gids")
            or args.get("model", {}).get("gids", [generate_id(), generate_id()]),
            "split": {
                "x": x,
                "y": y,
            },
        }

        default_gid = generate_id()
        return {
            "experiment_id": args["experiment_id"],
            "fcs_file_id": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", default_gid),
            "model": model,
            "names": args.get(
                "names",
                [args.get("name", default_gid) + suffix for suffix in [" (L)", " (R)"]],
            ),
            "tailored_per_file": args.get("tailored_per_file", False),
            "type": "SplitGate",
            "x_channel": args.get("x_channel"),
        }

    @classmethod
    def _generate_labels(cls, labels: List, experiment_id: str, x_channel: str):
        # set labels based on axis scale
        scaleset = ce.APIClient().get_scaleset(experiment_id)
        scale_min, scale_max = itemgetter("minimum", "maximum")(
            scaleset.scales[x_channel]
        )

        labels = [
            [scale_min + 0.1 * scale_max, 0.916],
            [scale_max - 0.1 * scale_max, 0.916],
        ]
        return labels
