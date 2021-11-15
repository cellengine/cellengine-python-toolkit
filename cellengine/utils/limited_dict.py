class LimitedDict(dict):
    """Extend this class and define `_keys` to limit the keys
    available in a dict.
    """

    _keys = set()

    def __init__(self, init_dict):
        for key in init_dict.keys():
            if key not in self._keys:
                raise ValueError(f"'{key}' is not a valid key.")
        dict.__init__(self, init_dict)

    def __setitem__(self, key, val):
        if key not in self._keys:
            raise KeyError(f"'{key}' is not a valid key.")
        dict.__setitem__(self, key, val)
