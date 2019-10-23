import attr
import pandas
import numpy
from .client import session
from . import _helpers


@attr.s(repr=False)
class Compensation(object):
    """A class representing a CellEngine compensation matrix. Can be applied to
    FCS files to compensate them.
    """
    _properties = attr.ib(default={}, repr=False)

    def __repr__(self):
        return "Compensation(_id=\'{0}\', name=\'{1}\')".format(self._id, self.name)

    _id = _helpers.GetSet('_id', read_only=True)

    name = _helpers.GetSet('name')

    experiment_id = _helpers.GetSet('experimentId')

    channels = _helpers.GetSet('channels')

    @property
    def N(self):
        return len(self.channels)

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
