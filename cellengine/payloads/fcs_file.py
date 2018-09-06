import attr
from typing import List

from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class _FcsFile(object):
    """A class containing CellEngine FCS file resource properties."""

    def __repr__(self):
        return "FcsFile(_id='{}', name='{}')".format(self._id, self.name)

    _properties = attr.ib(default={}, repr=False)

    @property
    def name(self):
        """Alias for `filename`."""
        return self._properties["filename"]

    @name.setter
    def name(self, val):
        self._properties["filename"] = val

    _id = GetSet("_id", read_only=True)

    compensation = GetSet("compensation")

    crc32c = GetSet("crc32c", read_only=True)

    event_count = GetSet("eventCount", read_only=True)

    experiment_id = GetSet("experimentId", read_only=True)

    filename = GetSet("filename")

    has_file_internal_comp = GetSet("hasFileInternalComp", read_only=True)

    header = GetSet("header", read_only=True)

    is_control = GetSet("isControl")

    md5 = GetSet("md5", read_only=True)

    panel = GetSet("panel")

    panel_name = GetSet("panelName")

    sample_name = GetSet("sampleName", read_only=True)

    size = GetSet("size", read_only=True)

    spill_string = GetSet("spillString", read_only=True)

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
        """Set new annotations.
        Warning: This will overwrite current annotations!
        """
        if type(val) is not dict or "name" and "value" not in val:
            raise TypeError('Input must be a dict with a "name" and a "value" item.')
        else:
            self._properties["annotations"] = val

    @property
    def channels(self) -> List:
        """Return all channels in the file"""
        return [f["channel"] for f in self.panel]
