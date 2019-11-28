import attr
import numpy
from cellengine import _helpers
from ._helpers import convert_dict
from . import Gates

import importlib
from abc import ABC
import munch


@attr.s(repr=False)
class Gate(ABC):
    """Basic abstract class for gates"""

    _posted = attr.ib(default=False)

    _properties = attr.ib(default=None)

    _population = attr.ib(default=None)

    def __repr__(self):
        return "{}(_id={}, name={})".format(self.type, self._id, self.name)

    @classmethod
    def create(cls, gates):
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
        # return [cls._create_gate(gate) for gate in res]

    @classmethod
    def _post_gate(cls, gate, experiment_id, create_population):
        """Post the gate, passing the factory as the class, which returns the correct subclass."""
        res = _helpers.base_create(
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

    _id = _helpers.GetSet("_id", read_only=True)

    name = _helpers.GetSet("name")

    type = _helpers.GetSet("type", read_only=True)

    experiment_id = _helpers.GetSet("experimentId", read_only=True)

    gid = _helpers.GetSet("gid")

    x_channel = _helpers.GetSet("xChannel")

    y_channel = _helpers.GetSet("yChannel")

    tailored_per_file = _helpers.GetSet("tailoredPerFile")

    fcs_file_id = _helpers.GetSet("fcsFileId")

    parent_population_id = _helpers.GetSet("parentPopulationId")

    names = _helpers.GetSet("names")

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
