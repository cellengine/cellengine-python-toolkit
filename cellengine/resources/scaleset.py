from __future__ import annotations
from numpy import arcsinh, clip, log10
from collections import defaultdict
from typing import Union, overload, Any, Dict, Optional, Callable

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from pandas import DataFrame

import cellengine as ce
from cellengine.resources.fcs_file import FcsFile


ScaleDict = TypedDict(
    "ScaleDict",
    {"type": str, "minimum": float, "maximum": float, "cofactor": Union[float, None]},
)

FLT_MIN = 1.17549435082228750797e-38


def apply_scale(item, scale: ScaleDict, clamp_q=False):
    _type = scale["type"]

    def bad_scale_error(_):
        raise ValueError(f"'{_type}' is not a valid scale type.")

    fn = defaultdict(
        lambda: bad_scale_error,
        {
            "LinearScale": lambda a: a,
            "LogScale": lambda a: log10(clip(a, a_min=FLT_MIN, a_max=None), dtype="f4"),
            "ArcSinhScale": lambda a: arcsinh(a / scale["cofactor"], dtype="f4"),
        },
    )

    if clamp_q:
        return fn[_type](clip(item, scale["minimum"], scale["maximum"]))
    else:
        return fn[_type](item)


class ScaleSet:
    def __init__(self, properties: Dict[str, Any]):
        self._properties = properties
        self._changes = set()
        self._orig_scales = properties["scales"].copy()

    @property
    def _id(self) -> str:
        return self._properties["_id"]

    @property
    def id(self) -> str:
        """Alias for ``_id``."""
        return self._properties["_id"]

    @property
    def experiment_id(self) -> str:
        return self._properties["experimentId"]

    @property
    def name(self) -> str:
        return self._properties["name"]

    @property
    def scales(self) -> Dict[str, ScaleDict]:
        return {s["channelName"]: s["scale"] for s in self._properties["scales"]}

    def __repr__(self):
        return "ScaleSet(_id='{}', name='{}')".format(self._id, self.name)

    @classmethod
    def get(cls, experiment_id: str) -> ScaleSet:
        return ce.APIClient().get_scaleset(experiment_id)

    def update(self):
        """Save changes to this ScaleSet to CellEngine.

        Warning: This API endpoint can change gates if their coordinates are
        affected by the scale parameters. You may need to re-query gates to
        synchronize your local state with CellEngine.
        """
        update_properties = {key: self._properties[key] for key in self._changes}
        if self.scales != self._orig_scales:
            update_properties["scales"] = [
                {"channelName": k, "scale": v} for k, v in self.scales.items()
            ]
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "scalesets", update_properties
        )
        self._properties = res["scaleSet"]
        self._changes = set()
        self._orig_scales = res["scaleSet"]["scales"].copy()

    def scale_for_channel(self, channel: str) -> Optional[ScaleDict]:
        """Get the scale for a channel.

        Args:
            channel: The channel name.

        Returns:
            The scale for the channel, or None if the channel is not in the
            scaleset.
        """
        return self.scales.get(channel)

    def scale_fn_for_channel(self, channel: str) -> Callable[[float], float]:
        """Get the scale function for a channel.

        Args:
            channel: The channel name.

        Returns:
            The scale function for the channel.
        """
        scale = self.scale_for_channel(channel)
        if scale is None:
            raise ValueError(f"Channel '{channel}' is not in this scaleset.")

        return lambda x: apply_scale(x, scale)

    @overload
    def apply(
        self, file: FcsFile, clamp_q: bool = False, in_place: Literal[True] = ...
    ) -> None:
        ...

    @overload
    def apply(
        self, file: FcsFile, clamp_q: bool = False, in_place: Literal[False] = ...
    ) -> DataFrame:
        ...

    def apply(self, file: FcsFile, clamp_q: bool = False, in_place: bool = True):
        """Apply the scaleset to a file.

        Args:
            file: The file to which this scaleset will be applied. See
                ``FcsFile.events``: the scaleset will be applied to the last
                result from ``FcsFile.get_events`` will be used if the file's
                events have already been retrieved.
            clamp_q: Clamp the output to the scale's minimum and maximum values.
            in_place: If True, updates `FcsFile.events` in-place; if False,
                returns a DataFrame.
        """
        dest = file.events if in_place else file.events.copy()

        for channel, scale in self.scales.items():
            if channel in dest.columns:
                dest[channel] = apply_scale(dest[channel], scale, clamp_q)

        if not in_place:
            return dest
