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
            res = session.get(f"experiments/{experiment_id}/fcsfiles",
                              params=query)
        res = session.get(f"experiments/{experiment_id}/fcsfiles")
        res.raise_for_status()
        files = [FcsFile(id=item['_id'], experiment_id=experiment_id,
                         properties=item) for item in res.json()]
        return files

    # @property
    # def info(self):
    #     return self._properties

    @property
    def path(self):
        base_path = f"experiments/{self.experiment_id}/fcsfiles"
        if self._id is not None:
            return f"{base_path}/{self._id}"
        else:
            return f"{base_path}"

    @property
    def events(self):
        """A DataFrame containing this file's data. This is fetched
        from the server on-demand the first time that this property is accessed.
        """
        if self._events is None:
#           TODO: name columns as $PnN; it appears to already do this, but I
#           need to test with several files
            fresp = self.session.get(f"experiments/{self.experiment_id}/fcsfiles/{self._id}.fcs")
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
        return self._properties['annotations']

#   TODO: important
    # compensation
