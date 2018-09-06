# Copyright 2018 Primity Bio
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
from datetime import datetime

ID_REGEX = re.compile(r"^[a-f0-9]{24}$", re.I)

def is_id(value):
    """Tests if ``value`` could be an _id."""
    return ID_REGEX.match(value) is True

def timestamp_to_datetime(value):
    """Converts ISO 8601 date+time UTC timestamps as returned by CellEngine to
    ``datetime`` objects."""
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

class _BaseApiObject(object):
    _BASE_PATH = ""
    """Abstract base API path"""

    def __init__(self, client, _id=None, name=None):
        # TODO fcsfiles use filename instead of name
        if not (bool(_id) ^ bool(name)):
            raise ValueError("Specify exactly one of `name` or `_id`")

        if _id is None and is_id(name):
            _id = name
            name = None

        self._client = client
        self._id = _id
        self.name = name
        self._properties = {}

    def load(self):
        """Loads the resource from the server using the _id or name property."""
        if self._id is None:
            self._load_by_name()
        else:
            res = self._client._s.get(self.path)
            res.raise_for_status()
            self._properties = res.json()

    def _load_by_name(self):
        # TODO does requests encode URI components for us?
        url = "{0}?query=eq(name,\"{1}\")&limit=2".format(self._BASE_PATH, self.name)
        res = self._client._s.get(url)
        res.raise_for_status()
        objs = res.json()
        if len(objs) > 1:
            err = "The name '{0}' is ambiguous, please use an _id instead".format(self.name)
            raise RuntimeError(err)
        self._properties = objs[0]
        self._id = self._properties.get("_id")

    @property
    def path(self):
        """Abstract getter"""
        raise NotImplementedError

    @property
    def created(self):
        return timestamp_to_datetime(self._properties.get("created"))
