import os
import re
import time
import binascii
from .client import session
from datetime import datetime


ID_REGEX = re.compile(r"^[a-f0-9]{24}$", re.I)


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


# TODO: add 'read/write' option
class GetSet:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        # print(self, '\n',  instance, '\n', owner)
        if instance is None:
            return self
        elif self.name in instance._properties.keys():
            return instance._properties[self.name]
        else:
            return None

    def __set__(self, instance, value):
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


def load(self, path, query='name'):
    if self._id is None:
        load_by_name(self, query)
    else:
        res = session.get(path)
        res.raise_for_status()
        content = res.json()
        if len(content) == 0:
            ValueError("Failed to load object from {0}".format(res.url))
        else:
            self._properties = content
            self.__dict__.update(self._properties)


def load_by_name(self, query):
    # TODO does requests encode URI components for us?
    url = "{0}?query=eq({1},\"{2}\")&limit=2".format(self.path, query, self.name)
    res = session.get(url)
    res.raise_for_status()
    objs = res.json()
    if len(objs) == 0:
        err = "No objects found with the name {0}.".format(self.name)
        raise RuntimeError(err)
    elif len(objs) > 1:
        err = "More than one object found with the name {0}, please use _id to query instead.".format(self.name)
        raise RuntimeError(err)
    else:
        self._properties = objs[0]
        self._id = self._properties.get("_id")


id_index = 0
def generate_id():
    """Generates a hexadecimal ID based on a mongoDB ObjectId"""
    global id_index
    timestamp = '{0:x}'.format(int(time.time()))
    seg1 = binascii.b2a_hex(os.urandom(5)).decode('ascii')
    seg2 = binascii.b2a_hex(os.urandom(2)+bytes([id_index])).decode('ascii')
    id_index += 1
    if id_index == 99:
        id_index = 0
    return timestamp+seg1+seg2


def list():
    """For general list queries.
    Wrapper around ``base_list`` for users.
    """
    pass
#   TODO


# TODO: pass list params to api
def base_list(url, classname, params=None, **kwargs):
    """API base list route
    This accepts queries to the ``params`` arg as a dict, but it will only
    return a valid object if the ``name`` or ``_id`` is not
    excluded. You can use the ``params`` arg to limit the number of
    returned objects, but the returned objects will always be
    complete; i.e. you can not prevent a property such as 'filename'
    from being loaded to the object.
    """
    res = session.get(url, params=params)
    res.raise_for_status()
    items = [classname(**kwargs, id=item['_id'], properties=item) for item in res.json()]
    return items


def base_get(url):
    # TODO: add by_name func for this
    res = session.get(url)
    res.raise_for_status()
    if res.apparent_encoding is not None:
        return res.json()
    else:
        return res


def base_create(url, body=None):
    """Create a new object. Accepts a dict of params for creation."""
    res = session.post(url, json=body)
    res.raise_for_status()


#   TODO: 500 error here
def base_update(url, body=None, **kwargs):
    session.patch(url, json=body, **kwargs)


def base_delete(url):
    res = session.delete(url)
    res.raise_for_status()
    return res


def created(self):
    return timestamp_to_datetime(self._properties.get("created"))
