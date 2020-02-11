import attr
import pandas
import fcsparser
from cellengine.utils import helpers
from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class FcsFile(object):
    """A class representing a CellEngine FCS file."""

    def __repr__(self):
        return "FcsFile(_id='{}', name='{}')".format(self._id, self.name)

    _properties = attr.ib(default={}, repr=False)

    _events = attr.ib(default=None)

    name = GetSet("filename")

    _id = GetSet("_id", read_only=True)

    experiment_id = GetSet("experimentId", read_only=True)

    panel_name = GetSet("panelName")

    event_count = GetSet("eventCount")

    has_file_internal_comp = GetSet("hasFileInternalComp")

    size = GetSet("size")

    md5 = GetSet("md5")

    filename = GetSet("filename")

    panel = GetSet("panel")

    compensation = GetSet("compensation")

    @property
    def annotations(self):
        """Return file annotations.
        New annotations may be added with file.annotations.append or
        redefined by setting file.annotations to a dict with a 'name'
        and 'value' key (i.e. {'name': 'plate row', 'value': 'A'}) or
        a list of such dicts.
        """
        return self._properties["annotations"]

    @annotations.setter
    def annotations(self, val):
        if type(val) is not dict or "name" and "value" not in val:
            raise TypeError('Input must be a dict with a "name" and a "value" item.')
        else:
            get_input = input("This will overwrite current annotations. Confirm y/n: ")
            if "y" in get_input.lower():
                self._properties["annotations"] = val

    @property
    def events(self):
        """A DataFrame containing this file's data. This is fetched
        from the server on-demand the first time that this property is accessed.
        """
        if self._events is None:
            fresp = helpers.base_get(
                "experiments/{0}/fcsfiles/{1}.fcs".format(self.experiment_id, self._id)
            )
            parser = fcsparser.api.FCSParser.from_data(fresp.content)
            self._events = pandas.DataFrame(parser.data, columns=parser.channel_names_n)
        return self._events

    @events.setter
    def events(self, val):
        self.__dict__["_events"] = val

    # API methods
    def update(self):
        """Save any changed data to CellEngine."""
        res = helpers.base_update(
            "experiments/{0}/compensations/{1}".format(self.experiment_id, self._id),
            body=self._properties,
        )
        self._properties.update(res)

