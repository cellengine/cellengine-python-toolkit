import os
import re
import time
import binascii
from .client import session
from datetime import datetime
from cellengine import ID_INDEX


ID_REGEX = re.compile(r"^[a-f0-9]{24}$", re.I)
first_cap_re = re.compile("(.)([A-Z][a-z]+)")
all_cap_re = re.compile("([a-z0-9])([A-Z])")


def check_id(_id):
    try:
        assert bool(ID_REGEX.match(_id)) is True
    except ValueError:
        print("Object has an invalid ID.")


def check_id(_id):
    try:
        assert bool(ID_REGEX.match(_id)) is True
    except ValueError:
        print('Object has an invalid ID.')


def camel_to_snake(name):
    s1 = first_cap_re.sub(r"\1_\2", name)
    return all_cap_re.sub(r"\1_\2", s1).lower()


def snake_to_camel(name):
    components = name.split("_")
    converted = components[0] + "".join(x.title() for x in components[1:])
    if converted == "Id":
        converted = "_id"
    return converted


def convert_dict(input_dict, input_style):
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


def timestamp_to_datetime(value):
    """Converts ISO 8601 date+time UTC timestamps as returned by CellEngine to
    ``datetime`` objects.
    """
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")


def today_timestamp():
    """Converts today's date to a ISO 8601 date+time UTC timestamp for deleting
    experiments.
    """
    return datetime.today().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def created(self):
    return timestamp_to_datetime(self._properties.get("created"))


def load(self, path, query="name"):
    if self._id is None:
        load_by_name(self, query)
    else:
        content = base_get(path)
        if len(content) == 0:
            ValueError("Failed to load object from {0}".format(self.path))
        else:
            self._properties = content
            self.__dict__.update(self._properties)


def load_by_id(_id):
    content = base_get("experiments/{0}".format(_id))
    return content


def load_by_name(self, query):
    # TODO does requests encode URI components for us?
    url = '{0}?query=eq({1},"{2}")&limit=2'.format(self.path, query, self.name)
    content = base_get(url)
    if len(content) == 0:
        raise RuntimeError("No objects found with the name {0}.".format(self.name))
    elif len(content) > 1:
        raise RuntimeError(
            "Multiple objects found with the name {0}, use _id to query instead.".format(
                self.name
            )
        )
    else:
        self._properties = content[0]
        self._id = self._properties.get("_id")
        self.__dict__.update(self._properties)


def load_experiment_by_name(name):
    content = base_get('experiments?query=eq(name, "{0}")&limit=2'.format(name))
    return load_object_by_name('__import__("cellengine").Experiment', content)


def load_fcsfile_by_name(experiment_id, name=None):
    content = base_get(
        'experiments/{0}/fcsfiles?query=eq(filename, "{1}")&limit=2'.format(
            experiment_id, name
        )
    )
    return load_object_by_name('__import__("cellengine").FcsFile', content)


def load_object_by_name(classname, content):
    if len(content) == 0:
        raise RuntimeError("No objects found.")
    elif len(content) > 1:
        raise RuntimeError("Multiple objects found; use _id to query instead.")
    elif type(content) is list:
        return make_class(classname, content[0])
    else:
        return make_class(classname, content)


def generate_id():
    """Generates a hexadecimal ID based on a mongoDB ObjectId"""
    global ID_INDEX
    timestamp = "{0:x}".format(int(time.time()))
    seg1 = binascii.b2a_hex(os.urandom(5)).decode("ascii")
    seg2 = binascii.b2a_hex(os.urandom(2) + bytes([ID_INDEX])).decode("ascii")
    ID_INDEX += 1
    if ID_INDEX == 99:
        ID_INDEX = 0
    return timestamp + seg1 + seg2


# TODO: pass list params to api
def base_list(url, classname):
    return make_class(classname, content=base_get(url))


def make_class(classname, content):
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


def base_get(url, params=None):
    res = session.get(url, params=params)
    res.raise_for_status()
    if res.apparent_encoding is not None:
        return res.json()
    else:
        return res


def base_create(
    url: str, expected_status: int, classname=None, json=None, params=None, **kwargs
):
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
    """
    res = session.post(url, json=json, params=params)
    if res.status_code == expected_status:
        data = parse_response(res)
        if classname:
            return make_class(classname, data)
        else:
            return data
    else:
        raise RuntimeError(res.content.decode())


def parse_response(content):
    content = content.json()
    return parse_list_or_single(content)


def parse_list_or_single(content):
    if type(content) is list:
        return parse_response_list(content)
    else:
        return parse_population_from_gate(content)


def parse_response_list(content):
    return [parse_list_or_single(item) for item in content]


def parse_population_from_gate(content):
    """Do-nothing for normal responses"""
    # TODO: return Population as another object
    if type(content) is dict:
        if "populations" in content.keys() or "population" in content.keys():
            # pop = content["population"] or content["populations"]
            content = content["gate"]
            return content
        else:
            return content


def base_update(url, body=None, classname=None, **kwargs):
    res = session.patch(url, json=body, **kwargs)
    res.raise_for_status()
    if classname:
        return make_class(classname, content=res.json())
    else:
        return res.json()


def base_delete(url):
    res = session.delete(url)
    res.raise_for_status()
    if res.content == b"":
        pass
    else:
        return res.json()
