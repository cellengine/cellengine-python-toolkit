from io import BufferedReader, BytesIO
from typing import BinaryIO, List, Optional, Union

import flowio
from flowio import FlowData, create_fcs
from numpy import reshape
from pandas.core.frame import DataFrame


class FcsFileIO:
    @classmethod
    def parse(
        cls, file: Union[BinaryIO, str], destination: str = ""
    ) -> Optional[DataFrame]:
        """Parse an FCS file to a Dataframe

        Args:
            file: Buffer-like or filepath (not a binary string)
            destination: If specified, writes directly to this filepath.
        """
        if destination and isinstance(file, (BufferedReader, BytesIO)):
            with open(destination, "wb") as loc:
                loc.write(file.read())
        else:
            f = cls.read(file)
            events = reshape(f.events, (-1, f.channel_count))  # type: ignore
            channels = [k["PnN"] for k in f.channels.values()]
            return DataFrame(events, columns=channels)

    @staticmethod
    def read(file: Union[BinaryIO, str]) -> FlowData:
        """Read an FCS file with flowio"""
        try:
            return flowio.FlowData(file)
        except AttributeError as e:
            raise FcsFileIOError("FCS file could not be read") from e

    @staticmethod
    def write(destination: str, file: DataFrame, channels: List[str]) -> None:
        """Write an FCS file

        Args:
            destination: File path to write
            file: The FCS file as a DataFrame
            channels: A list of channels (likely `file.columns`)
        """
        try:
            with open(destination, "wb") as f:
                create_fcs(f, file, channels)
        except Exception as e:
            raise FcsFileIOError("FCS file could not be written") from e


class FcsFileIOError(Exception):
    """Something is wrong reading or writing an FCS File"""
