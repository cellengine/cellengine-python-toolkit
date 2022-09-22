import flowio
from pandas import DataFrame
import numpy as np
from typing import BinaryIO, Union


def parse_fcs_file(file: Union[BinaryIO, str]) -> DataFrame:
    data = flowio.FlowData(file, True)
    events = np.reshape(data.events, (-1, data.channel_count))  # type: ignore
    channels = [k["PnN"] for k in data.channels.values()]
    return DataFrame(events, columns=channels, dtype="float32")
