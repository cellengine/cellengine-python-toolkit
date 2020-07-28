import attr
import importlib
from typing import Dict, List, Optional

import cellengine as ce
from cellengine.payloads.gate import _Gate
from cellengine.utils.api_client import APIClient
from cellengine.payloads.gate_utils import format_rectangle_gate


@attr.s(repr=False, slots=True)
class Gate(_Gate):
    def __init__(cls, *args, **kwargs):
        if cls is Gate:
            raise TypeError(
                "The Gate base class may not be directly instantiated. Use the .create() classmethod."
            )
        return object.__new__(cls, *args, **kwargs)

    _posted = attr.ib(default=False)

    @classmethod
    def get(
        cls, experiment_id: str, _id: Optional[str] = None, name: Optional[str] = None
    ):
        """Get a specific gate."""
        kwargs = {"name": name} if name else {"_id": _id}
        gate = ce.APIClient().get_gate(experiment_id, **kwargs)
        gate._posted = True
        return gate

    def delete(self):
        ce.APIClient().delete_gate(self.experiment_id, self._id)
        self._posted = False

    def update(self):
        """Save changes to this Gate to CellEngine.

        Args:
            inplace (bool): Update this entity or return a new one.

        Returns:
            Gate or None: If inplace is True, returns a new Gate.
            Otherwise, updates the current entity.
        """
        props = ce.APIClient().update_entity(
            self.experiment_id, self._id, "gates", body=self._properties
        )
        self._properties.update(props)

    def post(self):
        if self._posted is False:
            res = ce.APIClient().post_gate(
                self.experiment_id, self._properties, as_dict=True
            )
            self._properties.update(res)
            self._posted = True
        else:
            raise ValueError("Gate has already been posted to CellEngine.")

    @classmethod
    def build(cls, gates: Dict) -> List["_Gate"]:
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
            return [cls._build_gate(gate) for gate in gates]
        else:
            return cls._build_gate(gates)

    @classmethod
    def _build_gate(cls, gate):
        """Get the gate type and return instance of the correct subclass."""
        module = importlib.import_module(__name__)
        gate_type = getattr(module, gate["type"])
        return gate_type(properties=gate)

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
        return cls.build(
            format_rectangle_gate(
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
        )


class PolygonGate(Gate):
    """Basic concrete class for polygon gates"""

    pass


class EllipseGate(Gate):
    """Basic concrete class for ellipse gates"""

    pass


class RangeGate(Gate):
    """Basic concrete class for range gates"""

    pass


class QuadrantGate(Gate):
    """Basic concrete class for quadrant gates"""

    pass


class SplitGate(Gate):
    """Basic concrete class for split gates"""

    pass
