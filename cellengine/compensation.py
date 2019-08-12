import attr
from .client import session
import pandas as pd
import numpy as np
from ._helpers import load


@attr.s
class Compensation(object):
    """A class representing a CellEngine compensation matrix. Can be applied to
    FCS files to compensate them.
    """
    session = attr.ib(default=session, repr=False)
    name = attr.ib(default=None)
    _id = attr.ib(default=None)
    channels = attr.ib()
    query = attr.ib(default='name')
    experiment_id = attr.ib(kw_only=True)

    def __attrs_post_init__(self):
        """Load automatically by name or by id"""
        load(self, self.path)  # from _helpers

    @staticmethod
    def list(experiment_id, query=None):
        if query is not None:
            res = session.get(f"experiments/{experiment_id}/compensations",
                              params=query)
        res = session.get(f"experiments/{experiment_id}/compensations")
        res.raise_for_status()
        comps = [Compensation(id=item['_id'], experiment_id=experiment_id) for item in res.json()]
        return comps

    @property
    def channels(self):
        return self._properties.get('channels')

    @property
    def N(self):
        N = len(self.channels)
        return N

    @property
    def path(self):
        base_path = f"experiments/{self.experiment_id}/compensations"
        if self._id is not None:
            return f"{base_path}/{self._id}"
        else:
            return f"{base_path}"

    @property
    def dataframe(self):
        self.dataframe = pd.DataFrame(
            data=np.array(self._properties.get('spillMatrix').reshape((self.N, self.N)),
                          columns=self.channels,
                          index=self.channels)
        )

    def apply(self, file, inplace=True):
        """Compensates the file's data.

        :type parser: :class:`cellengine.FcsFile`
        :param parser: The FCS file to compensate.

        :type inplace: bool
        :param inplace: Compensate the file's data in-place.

        :returns: If :attr:`inplace` is True, nothing, else a DataFrame.
        """
        data = file.events

        # spill -> comp by inverting
        inverted = np.linalg.inv(self.dataframe)

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
