from __future__ import annotations
from cellengine.utils.readonly import readonly
from attr import define, field

from pandas import DataFrame

import cellengine as ce
from cellengine.utils.scale_utils import apply_scale
from cellengine.utils.scale_utils import ScaleDict
from cellengine.resources.fcs_file import FcsFile


@define
class ScaleSet:
    _id: str = field(on_setattr=readonly)
    experiment_id: str = field(on_setattr=readonly)
    name: str
    scales: ScaleDict

    def __repr__(self):
        return "ScaleSet(_id='{}', name='{}')".format(self._id, self.name)

    @property
    def client(self):
        return ce.APIClient()

    @property
    def path(self):
        return f"experiments/{self.experiment_id}/scalesets/{self._id}".rstrip("/None")

    @classmethod
    def get(cls, experiment_id: str) -> ScaleSet:
        return ce.APIClient().get_scaleset(experiment_id)

    def update(self):
        """Save changes to this Population to CellEngine."""
        res = self.client.update(self)
        self.__setstate__(res.__getstate__())  # type: ignore

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
            file = self.client.get_fcs_file(self.experiment_id, file)

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
