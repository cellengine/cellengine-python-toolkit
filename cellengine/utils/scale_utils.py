from collections import defaultdict
from typing import Dict

from numpy import arcsinh, clip, log10

from cellengine.utils.limited_dict import LimitedDict


class ScaleDict(LimitedDict):
    _keys = {"type", "minimum", "maximum", "cofactor"}


def apply_scale(scale: Dict, item, clamp_q=False):
    _type = scale["type"]

    def bad_scale_error(_):
        raise ValueError(f"'{_type}' is not a valid scale type.")

    fn = defaultdict(
        lambda: bad_scale_error,
        {
            "LinearScale": lambda a: a,
            "LogScale": lambda a: (0 if a <= 1 else log10(a)),
            "ArcSinhScale": lambda a: arcsinh(a / scale["cofactor"]),
        },
    )

    if clamp_q:
        return fn[_type](clip(item, scale["minimum"], scale["maximum"]))
    else:
        return fn[_type](item)
