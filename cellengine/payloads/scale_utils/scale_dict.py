from cellengine.utils.limited_dict import LimitedDict


class ScaleDict(LimitedDict):
    _keys = {"type", "minimum", "maximum", "cofactor"}
