import attr
from typing import Optional
from custom_inherit import doc_inherit

from cellengine.utils import helpers
from cellengine.utils.loader import Loader
from cellengine.utils.complex_population_creator import create_complex_population
from cellengine.resources.population import Population
from cellengine.resources.fcsfile import FcsFile
from cellengine.resources.compensation import Compensation
from cellengine.resources.gate import (
    Gate,
    RectangleGate,
    PolygonGate,
    EllipseGate,
    QuadrantGate,
    SplitGate,
    RangeGate,
)


@attr.s(repr=False, slots=True)
class Experiment(object):
    """A class representing a CellEngine experiment.

    Attributes
        _properties (:obj:`dict`): Experiment properties; reqired.
    """

    _properties = attr.ib()

    _id = helpers.GetSet("_id", read_only=True)

    name = helpers.GetSet("name")

    def __repr__(self):
        return "Experiment(_id='{0}', name='{1}')".format(self._id, self.name)

    @property
    def files(self):
        """List all files on the experiment"""
        url = "experiments/{0}/fcsfiles".format(self._id)
        return helpers.base_list(url, FcsFile)

    @property
    def comments(self):
        comments = self._properties["comments"]
        if type(comments) is not helpers.CommentList:
            self._properties["comments"] = helpers.CommentList(comments)
        return comments

    @comments.setter
    def comments(self, comments):
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
        return helpers.timestamp_to_datetime(self._properties.get("updated"))

    @property
    def deep_updated(self):
        return helpers.timestamp_to_datetime(self._properties.get("deepUpdated"))

    @property
    def deleted(self):
        if self._properties.get("deleted") is not None:
            return helpers.timestamp_to_datetime(self._properties.get("deleted"))

    @property
    def deleted(self, confirm=True):
        """Marks the experiment as deleted.

        Deleted experiments are permanently deleted after approximately
        7 days. Until then, deleted experiments can be recovered.
        """
        if confirm:
            self._properties["deleted"] = helpers.today_timestamp()
        else:
            pass

    public = helpers.GetSet("public")

    uploader = helpers.GetSet("uploader")

    primary_researcher = helpers.GetSet("primaryResearcher")

    active_compensation = helpers.GetSet("activeCompensation")

    locked = helpers.GetSet("locked")

    clone_source_experiment = helpers.GetSet("cloneSourceExperiment")

    revision_source_experiment = helpers.GetSet("revisionSourceExperiment")

    revisions = helpers.GetSet("revisions")

    per_file_compensations_enabled = helpers.GetSet("perFileCompensationsEnabled")

    tags = helpers.GetSet("tags")

    annotation_name_order = helpers.GetSet("annotationNameOrder")

    annotation_table_sort_columns = helpers.GetSet("annotationTableSortColumns")

    permissions = helpers.GetSet("permissions")

    @property
    def created(self):
        return helpers.timestamp_to_datetime(self._properties.get("created"))

    @property
    def files(self):
        """List all files on the experiment"""
        url = "experiments/{0}/fcsfiles".format(self._id)
        return helpers.base_list(url, FcsFile)

    def get_fcsfile(self, _id: Optional[str] = None, name: Optional[str] = None):
        return Loader.get_fcsfile(experiment_id=self._id, _id=_id, name=name)

    @property
    def populations(self):
        """List all populations in the experiment"""
        url = "experiments/{0}/populations".format(self._id)
        return helpers.base_list(url, Population)

    @property
    def compensations(self):
        url = "experiments/{0}/compensations".format(self._id)
        return helpers.base_list(url, Compensation)

    @property
    def gates(self):
        url = "experiments/{0}/gates".format(self._id)
        return helpers.base_list(url, Gate)

    # API methods
    def update(self):
        res = base_update("experiments/{0}", body = self._properties, classname = 'Experiment')

    # Gate Methods:

    @doc_inherit(Gate.delete_gates)
    def delete_gates(experiment_id, _id=None, gid=None, exclude=None):
        return Gate.delete_gates(self._id, **kwargs)

    @doc_inherit(RectangleGate.create)
    def create_rectangle_gate(self, *args, **kwargs):
        return RectangleGate.create(self._id, *args, **kwargs)

    @doc_inherit(PolygonGate.create)
    def create_polygon_gate(self, *args, **kwargs):
        return PolygonGate.create(self._id, *args, **kwargs)

    @doc_inherit(EllipseGate.create)
    def create_ellipse_gate(self, *args, **kwargs):
        return EllipseGate.create(self._id, *args, **kwargs)

    @doc_inherit(RangeGate.create)
    def create_range_gate(self, *args, **kwargs):
        return RangeGate.create(self._id, *args, **kwargs)

    @doc_inherit(SplitGate.create)
    def create_split_gate(self, *args, **kwargs):
        return SplitGate.create(self._id, *args, **kwargs)

    @doc_inherit(QuadrantGate.create)
    def create_quadrant_gate(self, *args, **kwargs):
        return QuadrantGate.create(self._id, *args, **kwargs)

    def create_complex_population(self, name, base_gate, gates):
        """Create a complex population. Pass Gate objects to the logical args."""
        return create_complex_population(self._id, name, base_gate, gates)
