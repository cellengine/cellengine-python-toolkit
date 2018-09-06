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

from ._helpers import _BaseApiObject, timestamp_to_datetime

class Experiment(_BaseApiObject):
    """A class representing a CellEngine experiment.
    """

    _BASE_PATH = "https://cellengine.com/api/v1/experiments"

    def __init__(self, client, name=None, _id=None):
        super(Experiment, self).__init__(client, _id, name)

    def __repr__(self):
        return "<Experiment: {0}>".format(self.name)

    @property
    def path(self):
        return "{0}/{1}".format(self._BASE_PATH, self._id)

    @property
    def comments(self):
        return self._properties.get("comments")

    @comments.setter
    def comments(self, comments):
        self._properties["comments"] = comments

    @property
    def updated(self):
        return timestamp_to_datetime(self._properties.get("updated"))

    @property
    def deep_updated(self):
        return timestamp_to_datetime(self._properties.get("deepUpdated"))

    @property
    def deleted(self):
        if self._properties.has_key("deleted"):
            return timestamp_to_datetime(self._properties.get("deleted"))
        return False

    def delete(self):
        """Marks this experiment as deleted. Deleted experiments are permanently
        deleted after approximately 7 days. Until then, deleted experiments can
        be recovered."""
        # TODO
        raise NotImplementedError

    @property
    def public(self):
        return self._properties.get("public")

    # uploader

    # primaryResearcher

    # activeCompensation

    @property
    def locked(self):
        return self._properties.get("locked")

    @property
    def clone_source_experiment(self):
        return self._properties.get("cloneSourceExperiment", None)

    @property
    def revision_source_experiment(self):
        return self._properties.get("revisionSourceExperiment", None)

    # revisions

    @property
    def per_file_compensations_enabled(self):
        return self._properties.get("perFileCompensationsEnabled")

    @property
    def tags(self):
        return self._properties.get("tags")

    # annotationNameOrder

    # annotationTableSortColumns

    # permissions
