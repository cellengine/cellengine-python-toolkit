import attr
from typing import Dict, List

import cellengine as ce
from cellengine.utils.helpers import GetSet

from abc import ABC
import munch


@attr.s(repr=False, slots=True)
class _Gate(ABC):
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

    _population = attr.ib(default=None)

    _properties = attr.ib(default={})

    def __repr__(self):
        return "{}(_id='{}', name='{}')".format(self.type, self._id, self.name)

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
        if type(model) is not _Gate._Munch:
            self._properties["model"] = munch.munchify(model, factory=self._Munch)
        return model

    @model.setter
    def model(self, val):
        model = self._properties["model"]
        model.update(val)

    class _Munch(munch.Munch):
        """Extend the Munch class for a dict-like __repr__"""

        # TODO: change this to show "Model()"

        def __repr__(self):
            return "{0}".format(dict.__repr__(self))
