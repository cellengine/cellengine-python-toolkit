import attr
from .client import session
import pandas
import fcsparser
from . import _helpers


@attr.s
class FcsFile(object):
    """A class representing a CellEngine FCS file."""
    name = attr.ib(default=None)
    _id = attr.ib(default=None)
    _session = attr.ib(default=session, repr=False)
    _properties = attr.ib(default={}, repr=False)
    _events = attr.ib(default=None, repr=False)
    experiment_id = attr.ib(kw_only=True)

    def __attrs_post_init__(self):
        """Load automatically by name or by id,
        Load ``name`` property if not yet loaded
        """
        _helpers.load(self, self.path, query='filename')  # from _helpers
        if self.name is None:
            self.name = self.filename

    @property
    def path(self):
        base_path = "experiments/{0}/fcsfiles".format(self.experiment_id)
        if self._id is not None:
            return "{0}/{1}".format(base_path, self._id)
        else:
            return "{0}".format(base_path)

    @property
    def events(self):
        """A DataFrame containing this file's data. This is fetched
        from the server on-demand the first time that this property is accessed.
        """
        if self._events is None:
            fresp = _helpers.base_get("experiments/{0}/fcsfiles/{1}.fcs".format(self.experiment_id, self._id))
            parser = fcsparser.api.FCSParser.from_data(fresp.content)
            self._events = pandas.DataFrame(parser.data, columns=parser.channel_names_n)

        return self._events

    panel_name = _helpers.GetSet('panelName')

    event_count = _helpers.GetSet('eventCount')

    has_file_internal_comp = _helpers.GetSet('hasFileInternalComp')

    size = _helpers.GetSet('size')

    md5 = _helpers.GetSet('md5')

    filename = _helpers.GetSet('filename')

    panel = _helpers.GetSet('panel')

    compensation = _helpers.GetSet('compensation')

    @property
    def annotations(self):
        """Return file annotations.
        New annotations may be added with file.annotations.append or
        redefined by setting file.annotations to a dict with a 'name'
        and 'value' key (i.e. {'name': 'plate row', 'value': 'A'}) or
        a list of such dicts.
        """
        return self._properties['annotations']

    @annotations.setter
    def annotations(self, val):
        if type(val) is not dict or 'name' and 'value' not in val:
            raise TypeError('Input must be a dict with a "name" and a "value" item.')
        else:
            get_input = input('This will overwrite current annotations. Confirm y/n: ')
            if 'y' in get_input.lower():
                self._properties['annotations'] = val
