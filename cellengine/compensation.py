import attr
import pandas
import numpy
from .client import session
from . import _helpers


@attr.s
class Compensation(object):
    """A class representing a CellEngine compensation matrix. Can be applied to
    FCS files to compensate them.
    """
    _session = attr.ib(default=session, repr=False)
    name = attr.ib(default=None)
    _id = attr.ib(default=None)
    _properties = attr.ib(default={}, repr=False)
    experiment_id = attr.ib(kw_only=True)

    def __attrs_post_init__(self):
        """Load automatically by name or by id"""
        _helpers.load(self, self.path)  # from _helpers

    @staticmethod
    def list(experiment_id, query=None):
        if query is not None:
            res = session.get("experiments/{0}/compensations".format(experiment_id),
                              params=query)
        res = session.get("experiments/{0}/compensations".format(experiment_id))
        res.raise_for_status()
        comps = [Compensation(id=item['_id'], experiment_id=experiment_id) for item in res.json()]
        return comps

    channels = _helpers.GetSet('channels')

    @property
    def N(self):
        N = len(self.channels)
        return N

    @property
    def path(self):
        base_path = "experiments/{0}/compensations".format(self.experiment_id)
        if self._id is not None:
            return "{0}/{1}".format(base_path, self._id)
        else:
            return "{0}".format(base_path)

    @property
    def dataframe(self):
        if hasattr(self, '_dataframe'):
            return self._dataframe
        else:
            self._dataframe = pandas.DataFrame(
                data=numpy.array(self._properties.get('spillMatrix')).reshape(self.N, self.N),
                                 columns=self.channels,
                                 index=self.channels)
            return self._dataframe

    def apply(self, file, inplace=True):
        """
        Compensates the file's data.

        :type parser: :class:`cellengine.FcsFile`
        :param parser: The FCS file to compensate.

        :type inplace: bool
        :param inplace: Compensate the file's data in-place.

        :returns: If :attr:`inplace` is True, nothing, else a DataFrame.
        """
        data = file.events

        # spill -> comp by inverting
        inverted = numpy.linalg.inv(self.dataframe)

        # Calculate matrix product for channels matching between file and comp
        comped = data[self.channels].dot(inverted)
        comped.columns = self.channels

        data.update(comped)

        if inplace:
            file._events = data
        else:
            return data

    def _repr_html_(self):
        return self.dataframe._repr_html_()
