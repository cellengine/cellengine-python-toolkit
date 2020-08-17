import numpy
import pandas

import cellengine as ce
from cellengine.payloads.compensation import _Compensation
from cellengine.resources.fcs_file import FcsFile


class Compensation(_Compensation):
    """A class representing a CellEngine compensation matrix. Can be applied to
    FCS files to compensate them.
    """

    @classmethod
    def get(cls, experiment_id: str, _id: str = None, name: str = None):
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_compensation(experiment_id, **kwargs)

    @classmethod
    def create(cls, experiment_id: str, compensation: dict):
        return ce.APIClient().post_compensation(experiment_id, compensation)

    def update(self, inplace=True):
        """Save changes to this Compensation to CellEngine.

        Args:
            inplace (bool): Update this entity or return a new one.

        Returns:
            Experiment or None: If inplace is True, returns a new Compensation.
            Otherwise, updates the current entity.
            """
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "compensations", body=self._properties
        )
        if inplace:
            self._properties.update(res)
        else:
            return self.__class__(res)

    def delete(self):
        return ce.APIClient().delete_entity(
            self.experiment_id, "compensations", self._id
        )

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

    @property
    def dataframe_as_html(self):
        """Return the compensation matrix dataframe as HTML."""
        return self.dataframe._repr_html_()

    def apply(self, file: FcsFile, inplace: bool = True, **params):
        """
        Compensates the file's data.

        Args:
            file (FcsFile): The FCS file to compensate.
            inplace (bool): Compensate the file's data in-place.
            params: Additional keyword args of form: [Additional Args][cellengine.ApiClient.ApiClient.download_fcs_file]

        Returns:
            DataFrame or None: if ``inplace=True``, returns nothing.
        """
        data = file.events(**params)

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
