import attr
import pandas
import numpy
from cellengine.utils import helpers
from cellengine.utils.helpers import GetSet


@attr.s(repr=False, slots=True)
class Compensation(object):
    """A class representing a CellEngine compensation matrix. Can be applied to
    FCS files to compensate them.
    """

    def __repr__(self):
        return "Compensation(_id='{}', name='{}')".format(self._id, self.name)

    _properties = attr.ib(default={}, repr=False)

    _dataframe = attr.ib(default=None, repr=False)

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

    experiment_id = GetSet("experimentId", read_only=True)

    channels = GetSet("channels")

    @property
    def N(self):
        return len(self.channels)

    @property
    def dataframe(self):
        """Get the compensation matrix as a Pandas DataFrame."""
        if getattr(self, "_dataframe") is not None:
            return self._dataframe
        else:
            self._dataframe = pandas.DataFrame(
                data=numpy.array(self._properties.get("spillMatrix")).reshape(
                    self.N, self.N
                ),
                columns=self.channels,
                index=self.channels,
            )
            return self._dataframe

    def dataframe_as_html(self):
        """Return the compensation matrix dataframe as HTML."""
        return self.dataframe._repr_html_()

    def apply(self, file, inplace: bool = True):
        """
        Compensates the file's data.

        Args:
            file (FcsFile): The FCS file to compensate.
            inplace (bool): Compensate the file's data in-place.

        Returns:
            DataFrame or None: if ``inplace=True``, returns nothing.
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

    # API methods
    def update(self):
        res = helpers.base_update(
            "experiments/{0}/compensations/{1}".format(self.experiment_id, self._id),
            body=self._properties,
        )
        self._properties.update(res)
