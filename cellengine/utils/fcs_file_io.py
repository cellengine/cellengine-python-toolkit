from typing import BinaryIO, Optional
from fcsparser.api import FCSParser
from pandas.core.frame import DataFrame


class FcsFileIO:
    @staticmethod
    def parse(file: BinaryIO, destination: str = "") -> Optional[DataFrame]:
        """Parse an FCS file to a Dataframe"""
        if destination:
            with open(destination, "wb") as loc:
                loc.write(file)
        else:
            parser = FCSParser.from_data(file)
            return DataFrame(parser.data, columns=parser.channel_names_n)
