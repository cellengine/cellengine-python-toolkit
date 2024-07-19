from __future__ import annotations
from typing import (
    List,
    Optional,
    TYPE_CHECKING,
    Tuple,
    Union,
    cast,
    overload,
    Any,
    Dict,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from numpy import array, linalg
from pandas import DataFrame

import cellengine as ce

if TYPE_CHECKING:
    from cellengine.resources.fcs_file import FcsFile


UncompensatedType = Literal[0]
UNCOMPENSATED: UncompensatedType = 0
"""Apply no compensation."""

FileInternalType = Literal[-1]
FILE_INTERNAL: FileInternalType = -1
"""
Use the file's internal compensation matrix, if available. If not available, an
error will be returned from API requests.
"""

PerFileType = Literal[-2]
PER_FILE: PerFileType = -2
"""
Use the compensation assigned to each individual FCS file. Not a valid value for
`FcsFile.compensation`.
"""

FileCompensations = Literal[UncompensatedType, FileInternalType]
"""Valid values for `FcsFile.compensation`."""

Compensations = Literal[UncompensatedType, FileInternalType, PerFileType]
"""Valid values for all compensation parameters except `fcsFile.compensation`."""


class Compensation:
    """A class representing a CellEngine compensation matrix."""

    def __init__(self, properties: Dict[str, Any]):
        self._properties = properties
        self._changes = set()

    @property
    def _id(self) -> str:
        return self._properties["_id"]

    @property
    def id(self) -> str:
        """Alias for ``_id``."""
        return self._properties["_id"]

    @property
    def experiment_id(self) -> str:
        return self._properties["experimentId"]

    @property
    def name(self) -> str:
        return self._properties["name"]

    @name.setter
    def name(self, name: str):
        self._properties["name"] = name
        self._changes.add("name")

    @property
    def channels(self) -> List[str]:
        return self._properties["channels"]

    @channels.setter
    def channels(self, channels: List[str]):
        self._properties["channels"] = channels
        self._changes.add("channels")

    @property
    def spill_matrix(self) -> List[float]:
        return self._properties["spillMatrix"]

    @spill_matrix.setter
    def spill_matrix(self, spill_matrix: List[float]):
        self._properties["spillMatrix"] = spill_matrix
        self._changes.add("spillMatrix")

    @property
    def dataframe(self) -> DataFrame:
        return DataFrame(
            array(self.spill_matrix).reshape(self.N, self.N),
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

    @classmethod
    def get(
        cls, experiment_id: str, _id: Optional[str] = None, name: Optional[str] = None
    ) -> Compensation:
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_compensation(experiment_id, **kwargs)

    @overload
    @classmethod
    def create(
        cls,
        experiment_id: str,
        name: str,
        channels: List[str],
        spill_matrix: List[float],
        dataframe: Optional[None],
    ) -> Compensation: ...

    @overload
    @classmethod
    def create(
        cls,
        experiment_id: str,
        name: str,
        *,
        dataframe: DataFrame,
    ) -> Compensation: ...

    @classmethod
    def create(
        cls,
        experiment_id: str,
        name: str,
        channels: Optional[List[str]] = None,
        spill_matrix: Optional[List[float]] = None,
        dataframe: Optional[DataFrame] = None,
    ) -> Compensation:
        """Create a new compensation.

        Specify either dataframe or channels and spill_matrix.

        Args:
            experiment_id (str): the ID of the experiment.
            name (str): The name of the compensation.
            channels (List[str]): The names of the channels to which this
                compensation matrix applies.
            spill_matrix (List[float]): The row-wise, square spillover matrix. The
                length of the array must be the number of channels squared.
            dataframe (DataFrame): A square pandas DataFrame with channel
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
        return Compensation(properties)

    def update(self):
        """Save changes to this Compensation to CellEngine."""
        update_properties = {key: self._properties[key] for key in self._changes}
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "compensations", update_properties
        )
        self._properties = res
        self._changes = set()

    def delete(self):
        ce.APIClient().delete_entity(self.experiment_id, "compensations", self._id)

    @property
    def dataframe_as_html(self):
        """Return the compensation matrix dataframe as HTML."""
        return self.dataframe._repr_html_()

    @overload
    def apply(self, file: FcsFile, inplace: Literal[True] = ..., **kwargs) -> None: ...

    @overload
    def apply(
        self, file: FcsFile, inplace: Literal[False] = ..., **kwargs
    ) -> DataFrame: ...

    def apply(
        self, file: FcsFile, inplace: Optional[bool] = True, **kwargs
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
        # [ the file's events have already been retrieved with the same
        #   kwargs provided here -> data := file.events
        # | true -> data := events retrieved from CellEngine ]
        if kwargs.items() == file._events_kwargs.items():
            data = file.events
        else:
            data = file.get_events(inplace=inplace, destination=None, **kwargs)

        # [ spillover := the inverse of the dataframe matrix ]
        spillover = DataFrame(
            linalg.inv(self.dataframe).astype("float32"),
            index=self.dataframe.index,
            columns=self.dataframe.columns,
        )

        # Store the multi-level index so we can restore it later
        original_columns = data.columns
        try:
            data.columns = data.columns.droplevel(1)
            # [ matching_cols := the columns of data that match the channels in
            #   the comp ]
            # Raises KeyError is data does not contain any channels in the comp
            matching_cols = data[self.channels]

            # [ comped := the compensated data ]
            # The column names of DataFrame and the index of other will be
            # aligned prior to the multiplication.
            comped = matching_cols.dot(spillover)

            if inplace:
                file._events.update(comped)
        finally:
            data.columns = original_columns

        if not inplace:
            copy = data.copy()
            copy.update(comped)
            return copy
