import attr
from abc import ABC
from munch import Munch, munchify

from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class _Gate(ABC):
    """
    A class containing Gate resource properties, and
    an abstract base class for specific gate types.

    Args: (For all gate types, refer to help for each gate for args
        specific to that gate.)

        experiment_id: The ID of the experiment to which to add the gate.
            Use when calling this as a static method; not needed when calling
            from an Experiment object
        name: The name of the gate
        x_channel: The name of the x channel to which the gate applies.
        gid: Group ID of the gate, used for tailoring. If this is not
            specified, then a new Group ID will be created. To create a
            tailored gate, you must specify the gid of the global tailored gate.
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

    def __repr__(self):
        if self.name:
            name = self.name
        else:
            name = str(self.names)
        return "{}(_id='{}', name='{}')".format(self.type, self._id, name)

    _id = GetSet("_id", read_only=True)

    _properties = attr.ib(default={})

    experiment_id = GetSet("experimentId", read_only=True)

    fcs_file_id = GetSet("fcsFileId")

    gid = GetSet("gid")

    name = GetSet("name")

    names = GetSet("names")

    parent_population_id = GetSet("parentPopulationId")

    tailored_per_file = GetSet("tailoredPerFile")

    type = GetSet("type", read_only=True)

    x_channel = GetSet("xChannel")

    y_channel = GetSet("yChannel")

    @property
    def model(self):
        model = self._properties["model"]
        if type(model) is not Munch:
            self._properties["model"] = munchify(model)
        return munchify(model)
