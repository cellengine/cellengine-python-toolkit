from __future__ import annotations
from typing import List, TYPE_CHECKING
from attr import define, field

from numpy import array, linalg
from pandas import DataFrame

import cellengine as ce
from cellengine.utils import readonly
from cellengine.utils.converter import converter


if TYPE_CHECKING:
    from cellengine.resources.fcs_file import FcsFile


@define
class Compensation:
    """A class representing a CellEngine compensation matrix.

    Can be applied to FCS files to compensate them.
    """

    _id: str = field(on_setattr=readonly)
    experiment_id: str = field(on_setattr=readonly)
    name: str
    channels: List[str]
    spill_matrix: List[int]

    @property
    def dataframe(self):
        return DataFrame(
            array(self.spill_matrix).reshape(self.N, self.N),  # type: ignore
            columns=self.channels,
            index=self.channels,
        )

    @dataframe.setter
    def dataframe(self, val: DataFrame):
        try:
            assert len(val.columns) == len(val.index)
            assert all(val.columns == val.index)
            self.channels = val.columns.to_list()
            self.spill_matrix = val.to_numpy().flatten().tolist()
        except Exception as e:
            raise e

    def __repr__(self):
        return f"Compensation(_id='{self._id}', name='{self.name}')"

    @property
    def path(self):
        return f"experiments/{self.experiment_id}/compensations/{self._id}".rstrip(
            "/None"
        )

    @property
    def client(self):
        return ce.APIClient()

    @property
    def N(self):
        return len(self.channels)

    @staticmethod
    def from_spill_string(spill_string: str) -> Compensation:
        """Creates a Compensation from a spill string (a file-internal compensation).
        This can be used with FcsFile.spill_string. The compensation is not
        saved to CellEngine.
        """
        arr = spill_string.split(",")
        length = int(arr.pop(0))
        channels = [arr.pop(0) for _ in range(length)]

        properties = {
            "_id": "",
            "channels": channels,
            "spillMatrix": [float(n) for n in arr],
            "experimentId": "",
            "name": "",
        }
        return converter.structure(properties, Compensation)

    def update(self):
        """Save changes to this Compensation to CellEngine."""
        res = self.client.update(self)
        self.__setstate__(res.__getstate__())  # type: ignore

    def delete(self):
        return self.client.delete_entity(self.experiment_id, "compensations", self._id)

    @property
    def dataframe_as_html(self):
        """Return the compensation matrix dataframe as HTML."""
        return self.dataframe._repr_html_()

    def apply(self, file: "FcsFile", inplace: bool = False, **kwargs):
        """
        Compensate an FcsFile's data.

        Args:
            file (FcsFile): The FCS file to compensate.
            inplace (bool): Compensate the file's data in-place.
            kwargs (Dict):
                All arguments accepted by `FcsFile.get_events` are accepted here.
        Returns:
            DataFrame: if ``inplace=True``, updates `FcsFile.events` for
                the target FcsFile
        """
        data = file.get_events(**kwargs, inplace=True, destination=None)

        # spill -> comp by inverting
        inverted = linalg.inv(self.dataframe)

        # Calculate matrix product for channels matching between file and comp
        if data and data[self.channels]:
            comped = data[self.channels]
            comped = comped.dot(inverted)  # type: ignore
            comped.columns = self.channels
            data.update(comped)
        else:
            raise IndexError(
                "No channels from this file match those in the compensation."
            )

        if inplace:
            file._events = data
        else:
            return data
