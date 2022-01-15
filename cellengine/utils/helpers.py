import re
from datetime import datetime
from typing import Any, Dict, List, Union


ID_REGEX = re.compile(r"^[a-f0-9]{24}$", re.I)
first_cap_re = re.compile("(.)([A-Z][a-z]+)")
all_cap_re = re.compile("([a-z0-9])([A-Z])")


def is_valid_id(_id: str) -> bool:
    return bool(ID_REGEX.match(_id))


def check_id(_id):
    try:
        assert is_valid_id(_id)
    except Exception as e:
        ValueError("Object has an invalid ID.", e)


def to_camel_case(snake_str: str) -> str:
    if snake_str == "_id":
        return snake_str
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def alter_keys(payload: Union[Dict[Any, Any], List[Dict[Any, Any]]], func):
    """Apply `func` to alter the keys of a dict or list of dicts."""
    empty = {}
    if isinstance(payload, list):
        return [alter_keys(p, func) for p in payload]
    elif type(payload) is dict:
        for k, v in payload.items():
            if isinstance(v, dict):
                empty[func(k)] = alter_keys(v, func)
            elif isinstance(v, list):
                empty[func(k)] = [alter_keys(p, func) for p in v]
            else:
                empty[func(k)] = v
        return empty
    else:
        return payload


def get_args_as_kwargs(cls_context, locals):
    # fmt: off
    arg_names = cls_context.create.__code__.co_varnames[
        1:cls_context.create.__code__.co_argcount
    ]
    # fmt: on
    return {key: locals[key] for key in arg_names}


class CommentList(list):
    """Modified list for CellEngine `comments` properties.

    Ensures that an appended comment dict has a newline after
    the last `insert` key.
    """

    def __init__(self, *args, **kwargs):
        super(CommentList, self).__init__(args[0])

    def append(self, comment):
        if comment[-1].get("insert").endswith("\n") is False:
            comment[-1].update(insert=comment[-1].get("insert") + "\n")
        super(CommentList, self).extend(comment)


class GetSet:
    """Generator class for getters and setters of API objects.

    Allows for much less verbose declaration of object properties from the
    underlying ``_properties`` dict, i.e.:

    ``name = helpers.GetSet("name")``

    instead of:

    ```
    @property
    def name(self):
        name = self._properties["name"]

    @name.setter
    def name(self, name):
    ```
    """

    def __init__(self, name, read_only=False):
        self.name = name
        self.read_only = read_only

    def __get__(self, instance, owner):
        if instance is None:
            return self
        elif self.name in instance._properties.keys():
            return instance._properties[self.name]
        else:
            return None

    def __set__(self, instance, value):
        if self.read_only is True:
            print("Cannnot set read-only property.")
        else:
            instance._properties[self.name] = value


def timestamp_to_datetime(value: str) -> datetime:
    """Converts ISO 8601 date+time UTC timestamps as returned by CellEngine to
    ``datetime`` objects.
    """
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")


def datetime_to_timestamp(value: datetime) -> str:
    """Converts ISO 8601 date+time UTC timestamps as returned by CellEngine to
    ``datetime`` objects.
    """
    return datetime.strftime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
