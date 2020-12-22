import attr
from typing import Dict

from cellengine.utils.helpers import (
    GetSet,
    CommentList,
    timestamp_to_datetime,
)


@attr.s(repr=False, slots=True)
class _Experiment(object):
    """A class containing CellEngine experiment resource properties."""

    def __repr__(self):
        return "Experiment(_id='{}', name='{}')".format(self._id, self.name)

    @property
    def comments(self):
        """Get comments for experiment.

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

    _properties = attr.ib()

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

    active_compensation = GetSet("activeCompensation")

    annotation_validators = GetSet("annotationValidators")

    annotation_name_order = GetSet("annotationNameOrder")

    annotation_table_sort_columns = GetSet("annotationTableSortColumns")

    clone_source_experiment = GetSet("cloneSourceExperiment", read_only=True)

    data = GetSet("data", read_only=True)

    locked = GetSet("locked", read_only=True)

    per_file_compensations_enabled = GetSet("perFileCompensationsEnabled")

    permissions = GetSet("permissions", read_only=True)

    primary_researcher = GetSet("primaryResearcher")

    revision_source_experiment = GetSet("revisionSourceExperiment", read_only=True)

    revisions = GetSet("revisions")

    sorting_spec = GetSet("sortingSpec")

    tags = GetSet("tags")

    uploader = GetSet("uploader", read_only=True)

    @property
    def created(self):
        return timestamp_to_datetime(self._properties.get("created"))
