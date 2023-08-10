from datetime import datetime
import re
from typing import Any, Dict, TypeVar
import numpy.typing as npt


ID_REGEX = re.compile(r"^[a-f0-9]{24}$", re.I)
first_cap_re = re.compile("(.)([A-Z][a-z]+)")
all_cap_re = re.compile("([a-z0-9])([A-Z])")
camel_re = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")


def is_valid_id(_id: str) -> bool:
    return bool(ID_REGEX.match(_id))


def check_id(_id):
    try:
        assert is_valid_id(_id)
    except Exception as e:
        ValueError("Object has an invalid ID.", e)


def to_camel_case(snake_str: str) -> str:
    if snake_str.startswith("_"):
        return snake_str
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_snake_case(camel_str: str) -> str:
    return camel_re.sub(r"_\1", camel_str).lower()


def get_args_as_kwargs(context, locals) -> Dict[str, Any]:
    """
    Args:
        context: `self` or `cls` in a class method
        locals: `locals()`
    """
    # fmt: off
    arg_names = context.create.__code__.co_varnames[
        1:context.create.__code__.co_argcount
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


def timestamp_to_datetime(value: str) -> datetime:
    """Converts an ISO 8601 date+time UTC timestamp to a ``datetime`` object."""
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")


def datetime_to_timestamp(value: datetime) -> str:
    """Converts a ``datetime`` object to an ISO 8601 date+time UTC timestamp."""
    return datetime.strftime(value, "%Y-%m-%dT%H:%M:%S.%fZ")


T = TypeVar("T", float, npt.NDArray)


def remove_keys_with_none_values(d: Dict[str, Any]) -> Dict[str, Any]:
    new_dict = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = remove_keys_with_none_values(v)
        if v is not None:
            new_dict[k] = v
    return new_dict
