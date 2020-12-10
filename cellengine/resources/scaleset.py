from pandas import DataFrame

import cellengine as ce
from cellengine.payloads.scaleset import _ScaleSet
from cellengine.resources.fcs_file import FcsFile
from cellengine.payloads.scale_utils.apply_scale import apply_scale


class ScaleSet(_ScaleSet):
    @classmethod
    def get(cls, experiment_id: str):
        return ce.APIClient().get_scaleset(experiment_id)

    def update(self):
        """Save changes to this ScaleSet to CellEngine."""
        self._save_scales()
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "scalesets", self._properties
        )
        self._properties.update(res)

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
                dest[channel] = data[channel].map(lambda a: apply_scale(scale, a, clamp_q))
            else:
                continue
        if in_place:
            file.events = dest
        else:
            return dest

    def _save_scales(self):
        """Save changes to scales to the object-internal _properties"""
        self._properties["scales"] = [
            {"channelName": key, "scale": val} for key, val in self.scales.items()
        ]
