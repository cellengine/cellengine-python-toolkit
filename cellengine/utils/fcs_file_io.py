from io import BufferedReader, BytesIO
from typing import BinaryIO, Optional, Union

import flowio
from flowio.flowdata import FlowData
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
        return flowio.FlowData(file)
