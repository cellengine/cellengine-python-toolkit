from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING, Tuple, Union, cast

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
    spill_matrix: List[float]

    @property
    def dataframe(self):
        return DataFrame(
            array(self.spill_matrix).reshape(self.N, self.N),  # type: ignore
            columns=self.channels,
            index=self.channels,
        )

    @dataframe.setter
    def dataframe(self, df: DataFrame):
        self.channels, self.spill_matrix = self._convert_dataframe(df)

    @staticmethod
    def _convert_dataframe(df: DataFrame) -> Tuple[List[str], List[float]]:
        try:
            assert all(df.columns == df.index)
            channels = cast(List[str], df.columns.tolist())
            spill_matrix = cast(List[float], df.to_numpy().flatten().tolist())
            return channels, spill_matrix
        except Exception:
            raise ValueError(
                "Dataframe must be a square matrix with equivalent index and columns."
            )

    def __repr__(self):
        return f"Compensation(_id='{self._id}', name='{self.name}')"

    @property
    def path(self):
        return f"experiments/{self.experiment_id}/compensations/{self._id}".rstrip(
            "/None"
        )

    @classmethod
    def from_dict(cls, data: dict):
        return converter.structure(data, cls)

    def to_dict(self):
        return converter.unstructure(self)

    @classmethod
    def get(
        cls, experiment_id: str, _id: Optional[str] = None, name: Optional[str] = None
    ) -> Compensation:
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_compensation(experiment_id, **kwargs)

    @classmethod
    def create(
        cls,
        experiment_id: str,
        name: str,
        channels: Optional[List[str]] = None,
        spill_matrix: Optional[List[float]] = None,
        dataframe: Optional[DataFrame] = None,
    ) -> Compensation:
        """Create a new compensation for this experiment

        Args:
            experiment_id (str): the ID of the experiment.
            name (str): The name of the compensation.
            channels (List[str]): The names of the channels to which this
                compensation matrix applies.
            spill_matrix (List[float]): The row-wise, square spillover matrix. The
                length of the array must be the number of channels squared.
            spill_matrix (DataFrame): A square pandas DataFrame with channel
                names in [df.index, df.columns].
        """
        if dataframe is None:
            if not (channels and spill_matrix):
                raise TypeError("Both 'channels' and 'spill_matrix' are required.")
        else:
            if spill_matrix or channels:
                raise TypeError(
                    "Only one of 'dataframe' or {'channels', 'spill_matrix'} "
                    "may be assigned."
                )
            else:
                channels, spill_matrix = cls._convert_dataframe(dataframe)

        body = {"name": name, "channels": channels, "spillMatrix": spill_matrix}
        return ce.APIClient().post_compensation(experiment_id, body)

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
        res = ce.APIClient().update(self)
        self.__setstate__(res.__getstate__())  # type: ignore

    def delete(self):
        return ce.APIClient().delete_entity(
            self.experiment_id, "compensations", self._id
        )

    @property
    def dataframe_as_html(self):
        """Return the compensation matrix dataframe as HTML."""
        return self.dataframe._repr_html_()

    def apply(
        self, file: FcsFile, inplace: bool = True, **kwargs
    ) -> Union[DataFrame, None]:
        """Compensate an FcsFile's data.

        Args:
            file (FcsFile): The FcsFile to compensate.
            inplace (bool): If True, modify the `FcsFile.events` with the result.
                If False, return the compensated events.
            **kwargs (Dict):
                All arguments accepted by `FcsFile.get_events` are accepted here.
                If the file's events have already been retrieved with the same
                kwargs provided here, those stored events will be used.
                Otherwise, the file's events will be retrieved from CellEngine.
        Returns:
            DataFrame: if ``inplace=True``, updates `FcsFile.events` for
                the target FcsFile
        """
        if kwargs.items() == file._events_kwargs.items():
            data = file.events
        else:
            data = file.get_events(inplace=inplace, destination=None, **kwargs)

        # Calculate matrix product for channels matching between file and comp
        cols = data.columns
        ix = list(
            filter(
                None,
                [channel if channel in cols else None for channel in self.channels],
            )
        )
        if any(ix):
            copy = data.copy()
            comped = copy[ix]
            comped = comped.dot(linalg.inv(self.dataframe))  # type: ignore
            comped.columns = ix
            copy.update(comped.astype(comped.dtypes[0]))
        else:
            raise IndexError(
                "No channels from this file match those in the compensation."
            )

        if inplace:
            file._events = copy
        return copy
