import flowio
from pandas import DataFrame
import numpy as np
from typing import BinaryIO, Union


def parse_fcs_file(file: Union[BinaryIO, str]) -> DataFrame:
    data = flowio.FlowData(file, True)
    events = np.reshape(data.events, (-1, data.channel_count))  # type: ignore
    pnn = data.pnn_labels
    pns = data.pns_labels
    return DataFrame(events, columns=[pnn, pns], dtype="float32")
