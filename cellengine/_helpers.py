import re
from .client import session
from datetime import datetime

ID_REGEX = re.compile(r"^[a-f0-9]{24}$", re.I)


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


def load(self, path):
    if self._id is None:
        load_by_name(self)
    else:
        res = session.get(path)
        res.raise_for_status()
        content = res.json()
        if len(content) == 0:
            ValueError("Failed to load object from {0}".format(res.url))
        else:
            self._properties = content


def load_by_name(self):
    # TODO does requests encode URI components for us?
    url = "{0}?query=eq({1},\"{2}\")&limit=2".format(self.path, self.query, self.name)
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


def created(self):
    return timestamp_to_datetime(self._properties.get("created"))


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
