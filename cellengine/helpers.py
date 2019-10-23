import os
import re
import time
import binascii
from functools import lru_cache
from .client import session
from datetime import datetime
from cellengine import ID_INDEX

cellengine = __import__(__name__.split(".")[0])


ID_REGEX = re.compile(r"^[a-f0-9]{24}$", re.I)
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def check_id(_id):
    try:
        assert bool(ID_REGEX.match(_id)) is True
    except ValueError:
        print("Object has an invalid ID.")


def check_id(_id):
    try:
        assert bool(ID_REGEX.match(_id)) is True
    except ValueError:
        print("Object has an invalid ID.")


def camel_to_snake(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def snake_to_camel(name):
    components = name.split('_')
    converted = components[0] + ''.join(x.title() for x in components[1:])
    if converted == "Id":
        converted = "_id"
    return converted


def convert_dict(input_dict, input_style):
    """Convert a dict from type 'snake' to type 'camel' or vice versa."""
    if input_style == 'snake_to_camel':
        convert = snake_to_camel
    elif input_style == 'camel_to_snake':
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
        if comment[-1].get('insert').endswith('\n') is False:
            comment[-1].update(insert=comment[-1].get('insert')+'\n')
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
            print('Cannnot set read-only property.')
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


def generate_id():
    """Generates a hexadecimal ID based on a mongoDB ObjectId"""
    global ID_INDEX
    timestamp = '{0:x}'.format(int(time.time()))
    seg1 = binascii.b2a_hex(os.urandom(5)).decode('ascii')
    seg2 = binascii.b2a_hex(os.urandom(2)+bytes([ID_INDEX])).decode('ascii')
    ID_INDEX += 1
    if ID_INDEX == 99:
        ID_INDEX = 0
    return timestamp+seg1+seg2


# TODO: pass list params to api
def base_list(url, classname):
    return make_class(classname, content=base_get(url))


def make_class(classname, content):
    classname = evaluate_classname(classname)
    if type(content) is dict:
        return classname(properties=content)
    elif type(content) is list:
        return [classname(properties=item) for item in content]


def evaluate_classname(classname):
    if type(classname) is str:
        classname = eval(classname)
    return classname


def base_get(url):
    res = session.get(url)
    res.raise_for_status()
    if res.apparent_encoding is not None:
        return res.json()
    else:
        return res


def base_create(classname, url, expected_status, json=None, params=None, **kwargs):
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
        return make_class(classname, data)
    else:
        raise Exception(res.content.decode())


def parse_response(content):
    content = content.json()
    if type(content) is list:
        return parse_response_list(content)
    else:
        return parse_population_from_gate(content)


def parse_response_list(content):
    return [parse_response(item) for item in content]


def parse_population_from_gate(content):
    """Do-nothing for normal responses"""
    # TODO: return Population as another object
    if type(content) is dict:
        if 'populations' in content.keys() or 'population' in content.keys():
            content = content['gate']
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
