from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from dataclasses_json.cfg import config
import numpy
from pandas import DataFrame

import cellengine as ce
from cellengine.utils.dataclass_mixin import DataClassMixin, ReadOnly


if TYPE_CHECKING:
    from cellengine.resources.fcs_file import FcsFile


@dataclass
class Compensation(DataClassMixin):
    """A class representing a CellEngine compensation matrix.

    Can be applied to FCS files to compensate them.
    """

    name: str
    channels: List[str]
    dataframe: DataFrame = field(
        metadata=config(
            field_name="spillMatrix",
            encoder=lambda x: x.to_numpy().flatten().tolist(),
            decoder=lambda x: numpy.array(x),
        )
    )
    _id: str = field(
        metadata=config(field_name="_id"), default=ReadOnly()
    )  # type: ignore
    experiment_id: str = field(default=ReadOnly())  # type: ignore

    def __post_init__(self):
        self.dataframe = DataFrame(
            self.dataframe.reshape(self.N, self.N),
            columns=self.channels,
            index=self.channels,
        )

    def __repr__(self):
        return f"Compensation(_id='{self._id}', name='{self.name}')"

    @property
    def N(self):
        return len(self.channels)

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
        return Compensation.from_dict(properties)

    def update(self):
        """Save changes to this Compensation to CellEngine."""
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "compensations", body=self.to_dict()
        )
        self.__dict__.update(Compensation.from_dict(res).__dict__)

    def delete(self):
        return ce.APIClient().delete_entity(
            self.experiment_id, "compensations", self._id
        )

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
        inverted = numpy.linalg.inv(self.dataframe)

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
