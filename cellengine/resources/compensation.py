from __future__ import annotations
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
    def get(cls, experiment_id: str, _id: str = None, name: str = None) -> Compensation:
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_compensation(experiment_id, **kwargs)

    @classmethod
    def create(cls, experiment_id: str, compensation: dict) -> Compensation:
        """Creates a compensation

        Args:
            experiment_id: ID of experiment that this compensation belongs to.
            compensation: Dict containing `channels` and `spillMatrix` properties.
        """
        return ce.APIClient().post_compensation(experiment_id, compensation)

    def update(self):
        """Save changes to this Compensation to CellEngine."""
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "compensations", body=self._properties
        )
        self._properties.update(res)

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
            params (Dict):
                All arguments accepted by `FcsFile.events` are accepted here.
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
