import re
from requests import Response
from typing import Dict, List, Union
from datetime import datetime


ID_REGEX = re.compile(r"^[a-f0-9]{24}$", re.I)
first_cap_re = re.compile("(.)([A-Z][a-z]+)")
all_cap_re = re.compile("([a-z0-9])([A-Z])")


def check_id(_id):
    try:
        assert bool(ID_REGEX.match(_id)) is True
    except Exception as e:
        ValueError("Object has an invalid ID.", e)


def camel_to_snake(name: str) -> str:
    s1 = first_cap_re.sub(r"\1_\2", name)
    return all_cap_re.sub(r"\1_\2", s1).lower()


def snake_to_camel(name: str) -> str:
    components = name.split("_")
    converted = components[0] + "".join(x.title() for x in components[1:])
    if converted == "Id":
        converted = "_id"
    return converted


def convert_dict(input_dict: Dict, input_style: str):
    """Convert a dict from type 'snake' to type 'camel' or vice versa."""
    if input_style == "snake_to_camel":
        convert = snake_to_camel
    elif input_style == "camel_to_snake":
        convert = camel_to_snake
    else:
        raise ValueError("Invalid input type")
    return dict(zip([convert(name) for name in input_dict.keys()], input_dict.values()))


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
    """ Generator class for getters and setters of API objects.

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


def today_timestamp() -> str:
    """Converts today's date to a ISO 8601 date+time UTC timestamp for deleting
    experiments.
    """
    return datetime.today().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
