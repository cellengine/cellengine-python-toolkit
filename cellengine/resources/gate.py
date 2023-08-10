from __future__ import annotations
import importlib
from cellengine.utils.types import (
    ApplyTailoringInsert,
    ApplyTailoringUpdate,
)
from math import pi
from typing import Any, Dict, List, Optional, Union, Tuple, overload

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from numpy import mean

import cellengine as ce
from cellengine.resources.population import Population
from cellengine.utils import parse_fcs_file_args
from cellengine.utils import generate_id
from cellengine.utils.helpers import (
    get_args_as_kwargs,
    remove_keys_with_none_values,
)

try:
    from collections.abc import Mapping
except ImportError:
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


class ApplyTailoringResult:
    def __init__(self):
        self.inserted: List[Gate] = []
        self.updated: List[Gate] = []
        self.deleted: List[str] = []


class Gate:
    """Do not construct directly; use the `Experiment.create_*_gate` and
    `__Gate.create()` methods."""

    def __init__(self, properties: Dict[str, Any]):
        self._properties = properties
        self._changes = set()

    @property
    def _id(self) -> str:
        return self._properties["_id"]

    @property
    def id(self) -> str:
        """Alias for ``_id``."""
        return self._properties["_id"]

    @property
    def gid(self) -> str:
        return self._properties["gid"]

    @property
    def experiment_id(self) -> str:
        return self._properties["experimentId"]

    @property
    def type(self) -> str:
        return self._properties["type"]

    @property
    def x_channel(self) -> str:
        return self._properties["xChannel"]

    @property
    def y_channel(self) -> Union[str, None]:
        return self._properties["yChannel"]

    @property
    def model(self) -> Dict:
        return self._properties["model"]

    @property
    def locked(self) -> bool:
        return self._properties["locked"]

    @locked.setter
    def locked(self, value: bool) -> None:
        self._properties["locked"] = value
        self._changes.add("locked")

    @property
    def tailored_per_file(self) -> bool:
        return self._properties["tailoredPerFile"]

    @property
    def fcs_file_id(self) -> Union[str, None]:
        return self._properties["fcsFileId"]

    @staticmethod
    def _format_gate(gate):
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
        return ce.APIClient().post_gates(
            experiment_id.pop(),
            formatted_gates,
            {"create_population": False},
        )

    def update(self) -> None:
        """Save changes to this Gate to CellEngine."""
        update_properties = {key: self._properties[key] for key in self._changes}
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "gates", update_properties
        )
        self._properties = res
        self._changes = set()

    def delete(self) -> None:
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

    def apply_tailoring(self, fcs_file_ids: List[str]) -> ApplyTailoringResult:
        """Apply this gate's tailoring (copy its geometry) to other FCS files."""
        payload = ce.APIClient().apply_tailoring(self.experiment_id, self, fcs_file_ids)
        ret = ApplyTailoringResult()
        [ret.inserted.append(self._synthesize_gate(i)) for i in payload["inserted"]]
        [ret.updated.append(self._synthesize_gate(i)) for i in payload["updated"]]
        [ret.deleted.append(i["_id"]) for i in payload["deleted"]]
        return ret

    def untailor(self) -> None:
        # TODO
        pass

    def _synthesize_gate(
        self,
        payload: Union[ApplyTailoringInsert, ApplyTailoringUpdate],
    ):
        gate = self._properties  # TODO review
        gate.update(payload)
        return Gate(gate)


class SimpleGate(Gate):
    """Abstract class for gates with a single region (rectangle, ellipse,
    polygon, range)."""

    @property
    def name(self) -> Union[str, None]:
        return self._properties["name"]

    @name.setter
    def name(self, value: str) -> None:
        self._properties["name"] = value
        self._changes.add("name")

    def __repr__(self):
        return f"{self.type}(_id='{self._id}', name='{self.name}')"


class CompoundGate(Gate):
    """Abstract class for gates with multiple regions (quadrants and splits)."""

    @property
    def names(self) -> Union[List[str], None]:
        return self._properties["names"]

    @names.setter
    def names(self, value: List[str]) -> None:
        self._properties["names"] = value
        self._changes.add("names")

    def __repr__(self):
        return f"{self.type}(_id='{self._id}', names='{self.names}')"


class RectangleGate(SimpleGate):
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
                gate and population if `create_population` is True.

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
            "createPopulation": kwargs.pop("create_population", True),
            "parentPopulationid": kwargs.pop("parent_population_id", None),
        }

        gate = cls._format(**kwargs)
        r = ce.APIClient().post_gate(experiment_id, gate, params)
        # assert isinstance(r, RectangleGate)
        return r

    @classmethod
    @exception_handler
    def _format(cls, **kwargs: Dict[str, Any]):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        x1 = args.get("x1", args.get("model", {}).get("rectangle", {}).get("x1"))
        x2 = args.get("x2", args.get("model", {}).get("rectangle", {}).get("x2"))
        y1 = args.get("y1", args.get("model", {}).get("rectangle", {}).get("y1"))
        y2 = args.get("y2", args.get("model", {}).get("rectangle", {}).get("y2"))
        if x1 is None or x2 is None or y1 is None or y2 is None:
            raise ValueError("x1, x2, y1 and y2 must be provided.")

        label = args.get("label", args.get("model", {}).get("label"))
        if label is None or label == []:
            label = [mean([x1, x2]), mean([y1, y2])]

        model = {
            "locked": args.get("locked", args.get("model", {}).get("locked", False)),
            "label": label,
            "rectangle": {"x1": x1, "x2": x2, "y1": y1, "y2": y2},
        }

        return {
            "experimentId": args["experiment_id"],
            "fcsFileId": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", generate_id()),
            "model": model,
            "name": args.get("name"),
            "tailoredPerFile": args.get("tailored_per_file", False),
            "type": "RectangleGate",
            "xChannel": args.get("x_channel"),
            "yChannel": args.get("y_channel"),
        }


class PolygonGate(SimpleGate):
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
            "createPopulation": kwargs.pop("create_population", True),
            "parentPopulationid": kwargs.pop("parent_population_id", None),
        }

        gate = cls._format(**kwargs)
        r = ce.APIClient().post_gate(experiment_id, gate, params)
        # assert isinstance(r, PolygonGate)
        return r

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        vertices = args.get("vertices", []) or args.get("model", {}).get(
            "polygon", {}
        ).get("vertices", [])

        label = args.get("label") or args.get("model", {}).get("label")
        if label is None or label == []:
            label = mean(vertices, axis=0).tolist()

        model = {
            "locked": args.get("locked", args.get("model", {}).get("locked", False)),
            "label": label,
            "polygon": {"vertices": vertices},
        }

        return {
            "experimentId": args["experiment_id"],
            "fcsFileId": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", generate_id()),
            "model": model,
            "name": args.get("name"),
            "tailoredPerFile": args.get("tailored_per_file", False),
            "type": "PolygonGate",
            "xChannel": args.get("x_channel"),
            "yChannel": args.get("y_channel"),
        }


class EllipseGate(SimpleGate):
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
            "createPopulation": kwargs.pop("create_population", True),
            "parentPopulationid": kwargs.pop("parent_population_id", None),
        }

        gate = cls._format(**kwargs)
        r = ce.APIClient().post_gate(experiment_id, gate, params)
        # assert isinstance(r, EllipseGate)
        return r

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        angle = args.get("angle", args.get("model", {}).get("ellipse", {}).get("angle"))
        major = args.get("major", args.get("model", {}).get("ellipse", {}).get("major"))
        minor = args.get("minor", args.get("model", {}).get("ellipse", {}).get("minor"))
        x = args.get("x")
        y = args.get("y")
        if x is not None and y is not None:
            center = [x, y]
        else:
            center = args.get(
                "center", args.get("model", {}).get("ellipse", {}).get("center")
            )
            assert isinstance(center, list)
            x, y = center

        label = args.get("label") or args.get("model", {}).get("label")
        if label is None or label == []:
            label = [x, y]

        model = {
            "locked": args.get("locked", args.get("model", {}).get("locked", False)),
            "label": label,
            "ellipse": {
                "angle": angle,
                "major": major,
                "minor": minor,
                "center": center,
            },
        }

        return {
            "experimentId": args["experiment_id"],
            "fcsFileId": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", generate_id()),
            "model": model,
            "name": args.get("name"),
            "tailoredPerFile": args.get("tailored_per_file", False),
            "type": "EllipseGate",
            "xChannel": args.get("x_channel"),
            "yChannel": args.get("y_channel"),
        }


class RangeGate(SimpleGate):
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
            "createPopulation": kwargs.pop("create_population", True),
            "parentPopulationid": kwargs.pop("parent_population_id", None),
        }

        gate = cls._format(**kwargs)
        r = ce.APIClient().post_gate(experiment_id, gate, params)
        # assert isinstance(r, RangeGate)
        return r

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        x1 = args.get("x1", args.get("model", {}).get("range", {}).get("x1"))
        x2 = args.get("x2", args.get("model", {}).get("range", {}).get("x2"))
        y = args.get("y", args.get("model", {}).get("range", {}).get("y", 0.5))
        if x1 is None or x2 is None:
            raise ValueError("x1 and x2 must be provided.")

        label = args.get("label", args.get("model", {}).get("label"))
        if label is None or label == []:
            label = [mean([x1, x2]), y]

        model = {
            "locked": args.get("locked", args.get("model", {}).get("locked", False)),
            "label": label,
            "range": {"x1": x1, "x2": x2, "y": y},
        }

        return {
            "experimentId": args["experiment_id"],
            "fcsFileId": parse_fcs_file_args(
                args.get("experiment_id"),
                args.get("tailored_per_file", False),
                args.get("fcs_file_id"),
                args.get("fcs_file"),
            ),
            "gid": args.get("gid", generate_id()),
            "model": model,
            "name": args.get("name"),
            "tailoredPerFile": args.get("tailored_per_file", False),
            "type": "RangeGate",
            "xChannel": args.get("x_channel"),
        }


class QuadrantGate(CompoundGate):
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
                QuadrantGate and a list of four Populations; otherwise, a
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
            "createPopulation": kwargs.pop("create_population", True),
            "parentPopulationid": kwargs.pop("parent_population_id", None),
        }

        gate = cls._format(**kwargs)
        r = ce.APIClient().post_gate(experiment_id, gate, params)
        # assert isinstance(r, QuadrantGate)
        return r

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        x = args.get("x", args.get("model", {}).get("quadrant", {}).get("x"))
        y = args.get("y", args.get("model", {}).get("quadrant", {}).get("y"))
        angles = (
            args.get("model", {})
            .get("quadrant", {})
            .get("angles", [0.0, pi / 2, pi, 3 * pi / 2])
        )
        labels = args.get("labels", args.get("model", {}).get("labels"))

        if labels is None or labels == []:
            labels = cls._get_default_label_coords(
                args["experiment_id"],
                args["x_channel"],
                args["y_channel"],
            )
        if not (
            isinstance(labels, list)
            and len(labels) == 4
            and all(len(label) == 2 for label in labels)
        ):
            raise ValueError("Labels must be a list of four length-2 lists.")

        model = {
            "locked": args.get("locked", args.get("model", {}).get("locked", False)),
            "labels": labels,
            "gids": args.get(
                "gids",
                args.get("model", {}).get(
                    "gids", [generate_id(), generate_id(), generate_id(), generate_id()]
                ),
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
            "experimentId": args["experiment_id"],
            "fcsFileId": parse_fcs_file_args(
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
            "tailoredPerFile": args.get("tailored_per_file", False),
            "type": "QuadrantGate",
            "xChannel": args.get("x_channel"),
            "yChannel": args.get("y_channel"),
        }

    @classmethod
    def _get_default_label_coords(
        cls, experiment_id: str, x_channel: str, y_channel: str
    ) -> List[List[float]]:
        scaleset = ce.APIClient().get_scaleset(experiment_id)
        x_scale_fn = scaleset.scale_fn_for_channel(x_channel)
        y_scale_fn = scaleset.scale_fn_for_channel(y_channel)

        return [
            [x_scale_fn(1e38), y_scale_fn(1e38)],
            [x_scale_fn(-1e38), y_scale_fn(1e38)],
            [x_scale_fn(-1e38), y_scale_fn(-1e38)],
            [x_scale_fn(1e38), y_scale_fn(-1e38)],
        ]


class SplitGate(CompoundGate):
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
            "createPopulation": kwargs.pop("create_population", True),
            "parentPopulationid": kwargs.pop("parent_population_id", None),
        }

        gate = cls._format(**kwargs)
        r = ce.APIClient().post_gate(experiment_id, gate, params)
        # assert isinstance(r, SplitGate)
        return r

    @classmethod
    @exception_handler
    def _format(cls, **kwargs):
        """Get relevant kwargs and shape into a gate model"""

        args = remove_keys_with_none_values(kwargs)

        x = args.get("x", args.get("model", {}).get("split", {}).get("x"))
        y = args.get("y", args.get("model", {}).get("split", {}).get("y", 0.5))

        labels = args.get("labels", args.get("model", {}).get("labels"))
        if labels is None or labels == []:
            labels = cls._get_default_label_coords(
                args["experiment_id"], args["x_channel"]
            )
        if not (
            isinstance(labels, list)
            and len(labels) == 2
            and all(len(label) == 2 for label in labels)
        ):
            raise ValueError("Labels must be a list of two length-2 lists.")

        model = {
            "locked": args.get("locked", args.get("model", {}).get("locked", False)),
            "labels": labels,
            "gids": args.get(
                "gids",
                args.get("model", {}).get("gids", [generate_id(), generate_id()]),
            ),
            "split": {
                "x": x,
                "y": y,
            },
        }

        default_gid = generate_id()
        return {
            "experimentId": args["experiment_id"],
            "fcsFileId": parse_fcs_file_args(
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
            "tailoredPerFile": args.get("tailored_per_file", False),
            "type": "SplitGate",
            "xChannel": args.get("x_channel"),
        }

    @classmethod
    def _get_default_label_coords(
        cls, experiment_id: str, x_channel: str
    ) -> List[List[float]]:
        scaleset = ce.APIClient().get_scaleset(experiment_id)
        x_scale_fn = scaleset.scale_fn_for_channel(x_channel)

        return [
            [x_scale_fn(-1e38), 1],
            [x_scale_fn(1e38), 1],
        ]
