from typing import BinaryIO, Optional
from fcsparser.api import FCSParser
from pandas.core.frame import DataFrame


def parse_fcs_file(file: BinaryIO, destination: str = "") -> Optional[DataFrame]:
    """Parse an FCS file to a Dataframe"""
    if destination:
        with open(destination, "wb") as loc:
            loc.write(file)
    else:
        parser = FCSParser.from_data(file)
        return DataFrame(parser.data, columns=parser.channel_names_n)
