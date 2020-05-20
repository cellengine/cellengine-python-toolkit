import attr
from typing import Optional, Dict, Union, List

from cellengine.utils.helpers import (
    GetSet,
    CommentList,
    timestamp_to_datetime,
)


@attr.s(repr=False, slots=True)
class _Experiment(object):
    """A class representing a CellEngine experiment.

    Attributes
        _properties (dict): Experiment properties; required for initialization.
    """

    _properties = attr.ib()

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

    def __repr__(self):
        return "Experiment(_id='{}', name='{}')".format(self._id, self.name)

    @property
    def comments(self):
        """Set comments for experiment.

        Defaults to overwrite; append new comments with
        experiment.comments.append(dict) with the form:
        dict = {"insert": "some text",
        "attributes": {"bold": False, "italic": False, "underline": False}}.
        """
        comments = self._properties["comments"]
        if type(comments) is not CommentList:
            self._properties["comments"] = CommentList(comments)
        return comments

    @comments.setter
    def comments(self, comments: Dict):
        """Sets comments for experiment.

        Defaults to overwrite; append new comments with
        experiment.comments.append(dict) with the form:
         dict = {"insert": "some text",
        "attributes": {"bold": False, "italic": False, "underline": False}}.
        """
        if comments.get("insert").endswith("\n") is False:
            comments.update(insert=comments.get("insert") + "\n")
        self._properties["comments"] = comments

    @property
    def updated(self):
        """
        The last time that the experiment was modified.
        This value is a shallow timestamp; it is not updated when descendant
        resources such as gates are modified. (See deepUpdated.)
        """
        return timestamp_to_datetime(self._properties.get("updated"))

    @property
    def deep_updated(self) -> str:
        """
        The last time that the experiment or any of its descendant
        resources (e.g. gates, scales) were modified. This property is
        eventually consistent; its value may not be updated instantaneously
        after a descendant resource is modified.
        """
        return timestamp_to_datetime(self._properties.get("deepUpdated"))

    @property
    def deleted(self) -> str:
        """
        The time when the experiment was moved to the trash. Experiments are
        permanently deleted approximately seven days after this time. Cannot be
        set on revision experiments, experiments that are locked or experiments
        with an active retention policy.
        """
        if self._properties.get("deleted") is not None:
            return timestamp_to_datetime(self._properties.get("deleted"))

    primary_researcher = GetSet("primaryResearcher")

    active_compensation = GetSet("activeCompensation")

    locked = GetSet("locked", read_only=True)

    clone_source_experiment = GetSet("cloneSourceExperiment", read_only=True)

    # TODO: retention_policy (Munch object, read_only=True)

    revision_source_experiment = GetSet("revisionSourceExperiment", read_only=True)

    revisions = GetSet("revisions")

    per_file_compensations_enabled = GetSet("perFileCompensationsEnabled")

    per_file_compensation_enabled = GetSet("perFileCompensationEnabled")

    # TODO: sorting_spec

    tags = GetSet("tags", read_only=True)

    annotation_name_order = GetSet("annotationNameOrder")

    annotation_table_sort_columns = GetSet("annotationTableSortColumns")

    # TODO: annotationValidators

    # TODO: make this a Munch class:
    permissions = GetSet("permissions")

    data = GetSet("data", read_only=True)

    uploader = GetSet("uploader", read_only=True)

    public = GetSet("public")

    @property
    def created(self):
        return timestamp_to_datetime(self._properties.get("created"))
