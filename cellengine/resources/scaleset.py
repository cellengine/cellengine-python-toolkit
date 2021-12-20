from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Union, overload
from typing_extensions import Literal

from dataclasses_json.cfg import config
from pandas import DataFrame

import cellengine as ce
from cellengine.resources.fcs_file import FcsFile
from cellengine.utils.dataclass_mixin import DataClassMixin, ReadOnly
from cellengine.utils.scale_utils import apply_scale
from cellengine.utils.scale_utils import ScaleDict


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
    name: str
    scales: Dict["str", Dict[str, Union[str, int]]] = field(
        metadata=config(encoder=encode_json_scale, decoder=decode_json_scale)
    )
    _id: str = field(
        metadata=config(field_name="_id"), default=ReadOnly()
    )  # type: ignore
    experiment_id: str = field(default=ReadOnly())  # type: ignore

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
        if "scaleSet" in res.keys():
            res = res["scaleSet"]
        self.__dict__.update(ScaleSet.from_dict(res).__dict__)

    # fmt: off
    @overload
    def apply(
        self, file: FcsFile, clamp_q: bool = False, in_place: Literal[True] = True
    ) -> None: ...

    @overload
    def apply(
        self, file: FcsFile, clamp_q: bool = False, in_place: Literal[False] = False
    ) -> DataFrame: ...
    # fmt: on

    def apply(
        self, file: Union[FcsFile, str], clamp_q: bool = False, in_place: bool = True
    ):
        """Apply the scaleset to a file.

        Args:
            file (_id or FcsFile): The file to which this scaleset will be
                applied.
            clamp_q (bool): Clamp the output to the scale's minimum and maximum
                values.
            in_place (bool): If True, updates the FcsFile.events; if
                False, returns a DataFrame
        """
        if isinstance(file, str):
            file = FcsFile.get(file)

        data = file.events
        dest = DataFrame()

        for channel, scale in self.scales.items():
            if channel in data.columns:
                dest[channel] = data[channel].map(  # type: ignore
                    lambda a: apply_scale(scale, a, clamp_q)
                )
        if in_place:
            file.events.update(dest)
        else:
            copy = data.copy()
            copy.update(dest)
            return copy
