import attr
from .client import session
import pandas as pd
import fcsparser
from ._helpers import load


@attr.s
class FcsFile(object):
    """A class representing a CellEngine FCS file."""
    _session = attr.ib(default=session, repr=False)
    name = attr.ib(default=None)
    query = attr.ib(default="filename", repr=False)
    _id = attr.ib(default=None)
    _properties = attr.ib(default={}, repr=False)
    _events = attr.ib(default=None, repr=False)
    experiment_id = attr.ib(kw_only=True)


    def __attrs_post_init__(self):
        """Load automatically by name or by id"""
        load(self, self.path)  # from _helpers

    @staticmethod
    def list(experiment_id, query=None):
        if query is not None:
            res = session.get("experiments/{0}/fcsfiles".format(experiment_id),
                              params=query)
        res = session.get("experiments/{0}/fcsfiles".format(experiment_id))
        res.raise_for_status()
        files = [FcsFile(id=item['_id'], experiment_id=experiment_id,
                         properties=item) for item in res.json()]
        return files

    # @property
    # def info(self):
    #     return self._properties

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
#           TODO: name columns as $PnN; it appears to already do this, but I
#           need to test with several files
            fresp = self.session.get("experiments/{0}/fcsfiles/{1}.fcs".format(self.experiment_id, self._id))
            parser = fcsparser.api.FCSParser.from_data(fresp.content)
            columns = parser.channel_names_n
            self._events = pd.DataFrame(parser.data, columns=columns)

        return self._events

    @property
    def panel_name(self):
        return self._properties['panelName']

    @property
    def event_count(self):
        return self._properties['eventCount']

    @property
    def has_file_internal_comp(self):
        return self._properties['hasFileInternalComp']

    @property
    def size(self):
        return self._properties['size']

    @property
    def md5(self):
        return self._properties['md5']

    @property
    def filename(self):
        return self._properties['filename']

    @filename.setter
    def filename(self, filename):
        self._properties['filename'] = filename

    @property
    def panel(self):
        return self._properties['panel']

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

    @property
    def compensation(self):
        if 'compensation' in self._properties.keys():
            return self._properties['compensation']
        else:
            return None
