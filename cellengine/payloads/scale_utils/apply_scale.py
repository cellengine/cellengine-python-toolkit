from collections import defaultdict
from numpy import log10, arcsinh, clip


def apply_scale(scale, item, clamp_q=False):
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
