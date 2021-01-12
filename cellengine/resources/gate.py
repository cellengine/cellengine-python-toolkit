from __future__ import annotations
import attr
import importlib
from typing import Dict, List, Optional
from math import pi

import cellengine as ce
from cellengine.utils.helpers import get_args_as_kwargs
from cellengine.payloads.gate import _Gate
from cellengine.payloads.gate_utils import (
    format_rectangle_gate,
    format_split_gate,
    format_polygon_gate,
    format_ellipse_gate,
    format_quadrant_gate,
    format_range_gate,
)


@attr.s(repr=False)
class Gate(_Gate):
    def __init__(cls, *args, **kwargs):
        if cls is Gate:
            raise TypeError(
                "The Gate base class may not be directly \
                instantiated. Use the .create() classmethod."
            )
        return object.__new__(cls, *args, **kwargs)

    @classmethod
    def get(
        cls, experiment_id: str, _id: Optional[str] = None, name: Optional[str] = None
    ) -> Gate:
        """Get a specific gate."""
        kwargs = {"name": name} if name else {"_id": _id}
        gate = ce.APIClient().get_gate(experiment_id, **kwargs)
        return gate

    def delete(self):
        ce.APIClient().delete_gate(self.experiment_id, self._id)

    def update(self):
        """Save changes to this Gate to CellEngine.  """
        props = ce.APIClient().update_entity(
            self.experiment_id, self._id, "gates", body=self._properties
        )
        self._properties.update(props)

    def post(self):
        res = ce.APIClient().post_gate(
            self.experiment_id, self._properties, as_dict=True
        )
        props, _ = self._separate_gate_and_population(res)
        self._properties.update(props)

    @classmethod
    def bulk_create(cls, experiment_id, gates: List) -> List[Gate]:
        if type(gates[0]) is dict:
            pass
        elif str(gates[0].__module__) == "cellengine.resources.gate":
            gates = [gate._properties for gate in gates]
        return ce.APIClient().post_gate(experiment_id, gates, create_population=False)

    @classmethod
    def factory(cls, gates: Dict) -> List["Gate"]:
        """Build a Gate object from a dict of properties.

        Args:
            experiment_id (str): The ID of the experiment to which to add the gate. Use
                when calling this as a static method; not needed when calling from an
                Experiment object.
            name (str): The name of the gate
            x_channel (str): The name of the x channel to which the gate applies.
            y_channel (str): The name of the y channel to which the gate applies.
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
            return [cls._build_gate(gate) for gate in gates]
        else:
            return cls._build_gate(gates)

    @classmethod
    def _build_gate(cls, gate):
        """Get the gate type and return instance of the correct subclass."""
        module = importlib.import_module(__name__)
        gate, _ = cls._separate_gate_and_population(gate)
        gate_type = getattr(module, gate["type"])
        return gate_type(properties=gate)

    @classmethod
    def _separate_gate_and_population(cls, gate):
        try:
            if "gate" in gate.keys():
                return gate["gate"], [k for k in gate.keys() if k != "gate"]
            else:
                return gate, None
        except KeyError:
            raise ValueError("Gate payload format is invalid")

    @staticmethod
    def delete_gates(
        experiment_id, _id: str = None, gid: str = None, exclude: str = None
    ) -> None:
        """Deletes a gate or a tailored gate family.

        Specify the top-level gid when working with compound gates (specifying
        the gid of a sector (i.e. one listed in ``model.gids``) will result in no
        gates being deleted). If ``_id`` is specified, only that gate will be
        deleted, regardless of the other parameters specified. May be called as
        a static method from cellengine.Gate or from an Experiment instance.

        Args:
            experiment_id (str): ID of experiment.
            _id (str): ID of gate.
            gid (str): ID of gate family.
            exclude (str): Gate ID to exclude from deletion.

        Example:
            ```python
            cellengine.Gate.delete_gates(experiment_id, gid = <gate family ID>)
            # or
            experiment.delete_gates(_id = <gate ID>)
            # or
            experiment.delete_gates(gid = <gate family ID>, exclude = <gate ID>)
            ```

        Returns:
            None

        """
        ce.APIClient().delete_gate(experiment_id, _id, gid, exclude)

    @staticmethod
    def update_gate_family(experiment_id, gid: str, body: Dict):
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

    def tailor_to(self, fcs_file_id):
        """Tailor this gate to a specific fcs_file."""
        self._properties.update(
            ce.APIClient().tailor_to(self.experiment_id, self._id, fcs_file_id)
        )


class RectangleGate(Gate):
    """Basic concrete class for Rectangle gates"""

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
        g = format_rectangle_gate(**get_args_as_kwargs(cls, locals()))
        return cls(g)


class PolygonGate(Gate):
    """Basic concrete class for polygon gates"""

    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        vertices: List[float],
        label: List = [],
        gid: str = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):
        g = format_polygon_gate(**get_args_as_kwargs(cls, locals()))
        return cls(g)


class EllipseGate(Gate):
    """Basic concrete class for ellipse gates"""

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
        g = format_ellipse_gate(**get_args_as_kwargs(cls, locals()))
        return cls(g)


class RangeGate(Gate):
    """Basic concrete class for range gates"""

    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        name: str,
        x1: float,
        x2: float,
        y: float = 0.5,
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
        g = format_range_gate(**get_args_as_kwargs(cls, locals()))
        return cls(g)


class QuadrantGate(Gate):
    """Basic concrete class for quadrant gates"""

    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        x: float,
        y: float,
        labels: List[str] = [],
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
    ):
        g = format_quadrant_gate(**get_args_as_kwargs(cls, locals()))
        return cls(g)


class SplitGate(Gate):
    """Basic concrete class for split gates"""

    @classmethod
    def create(
        cls,
        experiment_id: str,
        x_channel: str,
        name: str,
        x: float,
        y: float = 0.5,
        labels: List[str] = [],
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
        g = format_split_gate(**get_args_as_kwargs(cls, locals()))
        return cls(g)
