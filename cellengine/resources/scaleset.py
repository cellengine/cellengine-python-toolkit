from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Union

from dataclasses_json.cfg import config
from pandas import DataFrame

import cellengine as ce
from cellengine.payloads.scale_utils.apply_scale import apply_scale
from cellengine.payloads.scale_utils.scale_dict import ScaleDict
from cellengine.resources.fcs_file import FcsFile
from cellengine.utils.dataclass_mixin import DataClassMixin


def encode_json_scale(scales):
    """Encode a ScaleDict to JSON
    See https://github.com/lidatong/dataclasses-json#Overriding for more info.
    """
    return [{"channelName": key, "scale": val} for key, val in scales.items()]


def decode_json_scale(scales) -> Dict[str, ScaleDict]:
    """Decode a ScaleSet from JSON to a ScaleDict
    See https://github.com/lidatong/dataclasses-json#Overriding for more info.
    """
    return {item["channelName"]: ScaleDict(item["scale"]) for item in scales}


@dataclass
class ScaleSet(DataClassMixin):
    _id: str = field(metadata=config(field_name="_id"))
    experiment_id: str
    name: str
    scales: Dict["str", Dict[str, Union[str, int]]] = field(
        metadata=config(encoder=encode_json_scale, decoder=decode_json_scale)
    )

    def __repr__(self):
        return "ScaleSet(_id='{}', name='{}')".format(self._id, self.name)

    @classmethod
    def get(cls, experiment_id: str) -> ScaleSet:
        return ce.APIClient().get_scaleset(experiment_id)  # type: ignore

    def update(self):
        """Save changes to this ScaleSet to CellEngine."""
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "scalesets", self.to_dict()
        )
        self.__dict__.update(self.from_dict(res).__dict__)

    def apply(self, file, clamp_q=False, in_place=True):
        """Apply the scaleset to a file.

        Args:
            file (_id or FcsFile): The file to which this scaleset will be
                applied.
            clamp_q (bool): Clamp the output to the scale's minimum and maximum
                values.
            in_place (bool): If True, updates the FcsFile.events; if
                False, returns a DataFrame
        """
        if type(file) is not FcsFile:
            file = FcsFile.get(file)

        data = file.events
        dest = DataFrame()

        for channel, scale in self.scales.items():
            if channel in data.columns:
                dest[channel] = data[channel].map(  # type: ignore
                    lambda a: apply_scale(scale, a, clamp_q)
                )
        if in_place:
            file.events = dest
        else:
            return dest
