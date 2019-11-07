import attr

# from custom_inherit import doc_inherit

cellengine = __import__(__name__.split(".")[0])
from . import _helpers
from .population import Population
from .fcsfile import FcsFile
from .compensation import Compensation
from .gate import Gate

# from . import Gates

# from .complex_population_creator import ComplexPopulationRequest
from .complex_population_creator import create_complex_population


@attr.s(repr=False)
class Experiment(object):
    """A class representing a CellEngine experiment.

    Attributes
        _properties (:obj:`dict`): Experiment properties; reqired.
    """

    def __repr__(self):
        return "Experiment(_id='{0}', name='{1}')".format(self._id, self.name)

    _properties = attr.ib()

    _id = _helpers.GetSet("_id", read_only=True)

    name = _helpers.GetSet("name")

    @property
    def files(self):
        """List all files on the experiment"""
        url = "experiments/{0}/fcsfiles".format(self._id)
        return _helpers.base_list(url, FcsFile)

    @property
    def comments(self):
        comments = self._properties["comments"]
        if type(comments) is not _helpers.CommentList:
            self._properties["comments"] = _helpers.CommentList(comments)
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
        return _helpers.timestamp_to_datetime(self._properties.get("updated"))

    @property
    def deep_updated(self):
        return _helpers.timestamp_to_datetime(self._properties.get("deepUpdated"))

    @property
    def deleted(self):
        if self._properties.get("deleted") is not None:
            return _helpers.timestamp_to_datetime(self._properties.get("deleted"))

    @property
    def delete(self, confirm=True):
        """Marks the experiment as deleted.

        Deleted experiments are permanently deleted after approximately
        7 days. Until then, deleted experiments can be recovered.
        """
        if confirm:
            self._properties["deleted"] = _helpers.today_timestamp()
        else:
            pass

    public = _helpers.GetSet("public")

    uploader = _helpers.GetSet("uploader")

    primary_researcher = _helpers.GetSet("primaryResearcher")

    active_compensation = _helpers.GetSet("activeCompensation")

    locked = _helpers.GetSet("locked")

    clone_source_experiment = _helpers.GetSet("cloneSourceExperiment")

    revision_source_experiment = _helpers.GetSet("revisionSourceExperiment")

    revisions = _helpers.GetSet("revisions")

    per_file_compensations_enabled = _helpers.GetSet("perFileCompensationsEnabled")

    tags = _helpers.GetSet("tags")

    annotation_name_order = _helpers.GetSet("annotationNameOrder")

    annotation_table_sort_columns = _helpers.GetSet("annotationTableSortColumns")

    permissions = _helpers.GetSet("permissions")

    @property
    def created(self):
        return _helpers.timestamp_to_datetime(self._properties.get("created"))

    def get_fcsfile(self, _id=None, name=None):
        return Gates.get_fcsfile(self._id, _id=_id, name=name)

    @property
    def populations(self):
        """List all populations in the experiment"""
        url = "experiments/{0}/populations".format(self._id)
        return _helpers.base_list(url, Population)

    @property
    def compensations(self):
        url = "experiments/{0}/compensations".format(self._id)
        return _helpers.base_list(url, Compensation)

    @property
    def gates(self):
        url = "experiments/{0}/gates".format(self._id)
        return _helpers.base_list(url, Gate)

    # Gate Methods:

    # @doc_inherit(Gates.delete_gates)
    def delete_gates(self, *args, **kwargs):
        return getattr(Gates, "delete_gates")(self._id, *args, **kwargs)

    # @doc_inherit(Gates.create_rectangle_gate)
    def create_rectangle_gate(self, *args, **kwargs):
        return getattr(Gates, "create_rectangle_gate")(self._id, *args, **kwargs)

    # @doc_inherit(Gates.create_polygon_gate)
    def create_polygon_gate(self, *args, **kwargs):
        return getattr(Gates, "create_polygon_gate")(self._id, *args, **kwargs)

    # @doc_inherit(Gates.create_ellipse_gate)
    def create_ellipse_gate(self, *args, **kwargs):
        return getattr(Gates, "create_ellipse_gate")(self._id, *args, **kwargs)

    # @doc_inherit(Gates.create_range_gate)
    def create_range_gate(self, *args, **kwargs):
        return getattr(Gates, "create_range_gate")(self._id, *args, **kwargs)

    # @doc_inherit(Gates.create_split_gate)
    def create_split_gate(self, *args, **kwargs):
        return getattr(Gates, "create_split_gate")(self._id, *args, **kwargs)

    # @doc_inherit(Gates.create_quadrant_gate)
    def create_quadrant_gate(self, *args, **kwargs):
        return getattr(Gates, "create_quadrant_gate")(self._id, *args, **kwargs)

    def create_complex_population(self, base_gate, name, gates):
        return create_complex_population(self._id, base_gate, name, gates)


#     def create_complex_population(
#         self,
#         name,
#         base_gate,
#         and_gates=None,
#         or_gates=None,
#         not_gates=None,
#         xor_gates=None,
#     ):
#         """Create a complex population. Pass Gate objects to the logical args."""
#         return Complex_Population_Request().create_complex_population(
#             self._id, name, base_gate, and_gates, or_gates, not_gates, xor_gates
#         )
