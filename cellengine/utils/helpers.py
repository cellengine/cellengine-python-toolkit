import re
from requests.exceptions import RequestException, HTTPError
from requests import Response
from typing import Dict, List, Union
from cellengine.client import session
from cellengine.utils.classes import ResourceFactory
from datetime import datetime

cellengine = __import__(__name__.split(".")[0])

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


# TODO: pass list params to api
def base_list(url, classname):
    return ResourceFactory.load(base_get(url))


def make_class(classname: Union[str, "APIObject"], content: Union[Dict, List]):
    """Instantiate an object with data from the CE API.
    Accepts the class name as a string or type.
    """
    classname = evaluate_classname(classname)
    if type(content) is dict:
        return classname(properties=content)
    elif type(content) is list:
        return [classname(properties=item) for item in content]


def evaluate_classname(classname):
    if type(classname) is str:
        classname = eval(classname)
    return classname


def base_get(url, params: dict = None) -> Response:
    res = session.get(url, params=params)
    res.raise_for_status()
    if res.apparent_encoding is not None:
        try:
            return res.json()
        except Exception:
            # Return the non-JSON content
            return res.content
    else:
        return res


def base_post(url: str, json: Dict = None, params: Dict = None, **kwargs):
    res = session.post(url, json=json, params=params, **kwargs)
    try:
        res.raise_for_status()
        return res
    except HTTPError as e:
        raise RequestException(res.content, e)


def base_create(
    url: str,
    expected_status: int,
    classname: Union[str, "APIObject"] = None,
    json: Dict = None,
    params: Dict = None,
    files: Dict = None,
    **kwargs
) -> Union[Response, str]:
    """Create a new object.

    Args:
        classname: Name of the CellEngine class returned by the API.
        url: Path of object to be created.
        json: Body of object to be created.
        params: Extra parameters to send along with http request (i.e.
        createPopulation=True)
        **kwargs: Class-specific kwargs for the class to be created.

    Returns:
        A loaded data class corresponding to the passed classname. Note that
        the most likely **kwarg to be passed is ``experiment_id``; this is a
        required init param for Gate, Population, Compensation, and similar
        objects, but not for Experiment.
        If classname is not specified, returns a Response object.
    """
    res = base_post(url, json=json, params=params, **kwargs)
    if res.status_code == expected_status:
        data = parse_response(res)
        if classname:
            return make_class(classname, data)
        else:
            return data
    else:
        raise RuntimeError(res.content.decode())


def parse_response(content: Response) -> Union[List, str]:
    content = content.json()
    return parse_list_or_single(content)


def parse_list_or_single(content: Union[List, str]) -> str:
    if type(content) is list:
        return parse_response_list(content)
    else:
        return parse_population_from_gate(content)


def parse_response_list(content: List[List]) -> List:
    """Parse sublists"""
    return [parse_list_or_single(item) for item in content]


def parse_population_from_gate(content: Dict) -> str:
    """Do-nothing for normal responses"""
    # TODO: return Population as another object
    if type(content) is dict:
        if "populations" in content.keys() or "population" in content.keys():
            # pop = content["population"] or content["populations"]
            content = content["gate"]
            return content
        else:
            return content


def base_update(url, body: Dict = None, **kwargs) -> str:
    res = session.patch(url, json=body, **kwargs)
    res.raise_for_status()
    return res.json()


def base_delete(url: str) -> str:
    res = session.delete(url)
    res.raise_for_status()
    if res.content == b"":
        pass
    else:
        return res.json()
