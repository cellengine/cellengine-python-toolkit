from io import BufferedReader, BytesIO
from typing import BinaryIO, Dict, List, Optional, Tuple, Union, overload

import flowio
from flowio import FlowData, create_fcs
from numpy import reshape
from pandas.core.frame import DataFrame


class FcsFileIO:
    def __init__(self, flow_data: FlowData):
        self.flow_data = flow_data

    @property
    def dataframe(self) -> DataFrame:
        f = self.flow_data
        events = reshape(f.events, (-1, f.channel_count))  # type: ignore
        channels = [k["PnN"] for k in f.channels.values()]
        return DataFrame(events, columns=channels)

    @property
    def flowio(self):
        return self.flow_data

    @classmethod
    def read(cls, file: Union[BinaryIO, str, bytes]):
        """Read an FCS file with flowio"""
        try:
            return cls(flowio.FlowData(file))
        except AttributeError as e:
            raise FcsFileIOError("FCS file could not be read") from e

    @classmethod
    def parse(
        cls, file: Union[BinaryIO, str], return_reagents: bool = False
    ) -> Union[DataFrame, Tuple[DataFrame, Dict[str, str]]]:
        """Parse an FCS file to a Dataframe

        Args:
            file: Buffer-like or filepath (not a binary string)
            return_reagents: Also return eagents in a dict of
                {'channel_name': reagent}. If true, returns a tuple of
                (DataFrame, reagents)
        """
        f = cls.read(file)
        if return_reagents:
            reagents = {
                v.get("PnN"): v.get("PnS", "") for _, v in f.flowio.channels.items()
            }
            return f.dataframe, reagents
        return f.dataframe

    def save(self, destination: str) -> None:
        self.flow_data.write_fcs(destination)

    @overload
    def write(
        *,
        destination: str,
        file: DataFrame,
        channels: Optional[List[str]] = [],
        reagents: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        ...

    @overload
    def write(*, destination: str, file: BinaryIO) -> None:
        ...

    @staticmethod
    def write(
        *,
        destination: str,
        file: Union[DataFrame, BinaryIO],
        channels: Optional[List[str]] = None,
        reagents: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        """Write an FCS file

        Args:
            destination: File path to write
            file: The FCS file as a DataFrame
            channels: A list of channels (likely `file.columns`)
            reagents: A list of reagents, the same length as `channels`
            metadata: Metadata keys:values
        """
        try:
            if isinstance(file, DataFrame):
                if not channels:
                    channels = list(file.columns)
                with open(destination, "wb") as f:
                    create_fcs(
                        f,
                        file.to_numpy().flatten().tolist(),
                        channels,
                        reagents,
                        metadata,
                    )
            elif isinstance(file, (BufferedReader, BytesIO)):
                with open(destination, "wb") as loc:
                    loc.write(file.read())
        except Exception as e:
            raise FcsFileIOError("FCS file could not be written") from e


class FcsFileIOError(Exception):
    """Something is wrong reading or writing an FCS File"""
