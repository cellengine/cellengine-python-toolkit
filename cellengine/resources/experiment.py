import attr
from typing import Optional, Dict, Union, List
from custom_inherit import doc_inherit

from cellengine.utils import helpers
from cellengine.utils.helpers import GetSet, CommentList
from cellengine.utils.loader import Loader
from cellengine.utils.complex_population_creator import create_complex_population
from cellengine.resources.population import Population
from cellengine.resources.fcsfile import FcsFile
from cellengine.resources.compensation import Compensation
from cellengine.resources.attachments import Attachment
from cellengine.resources.statistics import get_statistics
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
        _properties (dict): Experiment properties; required for initialization.
    """

    def __repr__(self):
        return "Experiment(_id='{}', name='{}')".format(self._id, self.name)

    _properties = attr.ib()

    _id = GetSet("_id", read_only=True)

    name = GetSet("name")

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
        return helpers.timestamp_to_datetime(self._properties.get("updated"))

    @property
    def deep_updated(self) -> str:
        """
        The last time that the experiment or any of its descendant
        resources (e.g. gates, scales) were modified. This property is
        eventually consistent; its value may not be updated instantaneously
        after a descendant resource is modified.
        """
        return helpers.timestamp_to_datetime(self._properties.get("deepUpdated"))

    @property
    def deleted(self) -> str:
        """
        The time when the experiment was moved to the trash. Experiments
        are permanently deleted approximately seven days after this time. Only
        modifiable by the primary_researcher. Cannot be set on revision
        experiments, experiments that are locked or experiments with an active
        retention policy.
        """
        if self._properties.get("deleted") is not None:
            return helpers.timestamp_to_datetime(self._properties.get("deleted"))

    @property
    def delete(self, confirm=False):
        """Marks the experiment as deleted.

        Deleted experiments are permanently deleted after approximately
        7 days. Until then, deleted experiments can be recovered.
        """
        if confirm:
            self._properties["deleted"] = helpers.today_timestamp()

    @property
    def undelete(self):
        """Remove a scheduled deletion."""
        if self._properties.get("deleted") is not None:
            self._properties["delete"] = None

    public = GetSet("public")

    primary_researcher = GetSet("primaryResearcher")

    # TODO: make this return a compensation
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

    @property
    def created(self):
        return helpers.timestamp_to_datetime(self._properties.get("created"))

    # Methods:

    @property
    def files(self):
        """List all files on the experiment

        Returns:
            List[FcsFile]: A list of fcsfiles on this experiment.
        """
        url = "experiments/{0}/fcsfiles".format(self._id)
        return helpers.base_list(url, FcsFile)

    def get_fcsfile(self, _id: Optional[str] = None, name: Optional[str] = None):
        """Get a single fcsfile

        Returns:
            FcsFile
        """
        return Loader.get_fcsfile(experiment_id=self._id, _id=_id, name=name)

    @property
    def populations(self):
        """List all populations in the experiment

        Returns:
            List[Population]: A list of populations on this experiment.
        """
        url = "experiments/{0}/populations".format(self._id)
        return helpers.base_list(url, Population)

    @property
    def compensations(self):
        """List all compensations on the experiment

        Returns:
            List[Compensation]: A list of compensations on this experiment.
        """
        url = "experiments/{0}/compensations".format(self._id)
        return helpers.base_list(url, Compensation)

    @property
    def gates(self):
        """List all gates on the experiment

        Returns:
            List[Gate]: A list of gates on this experiment.
        """
        url = "experiments/{0}/gates".format(self._id)
        return helpers.base_list(url, Gate)

    @property
    def attachments(self):
        """List all attachments on the experiment

        Returns:
            List[Attachment]: A list of attachments on this experiment.
        """
        url = "experiments/{0}/attachments".format(self._id)
        return helpers.base_list(url, Attachment)

    def get_statistics(
        self,
        statistics: Union[str, List[str]],
        channels: List[str],
        q: float = None,
        annotations: bool = False,
        compensation_id: str = None,
        fcs_file_ids: List[str] = None,
        format: str = "json",
        layout: str = None,
        percent_of: Union[str, List[str]] = None,
        population_ids: List[str] = None,
    ):
        return get_statistics(
            self._id,
            statistics,
            channels,
            q,
            annotations,
            compensation_id,
            fcs_file_ids,
            format,
            layout,
            percent_of,
            population_ids,
        )

    # API Methods:

    def update(self):
        """Save changes to this Experiment object to CellEngine.

        Returns:
            None: Updates the Experiment on CellEngine and then
                  synchronizes the properties with the current Experiment object.

        """
        res = helpers.base_update(
            "experiments/{0}".format(self._id), body=self._properties
        )
        self._properties.update(res)

    # Gate Methods:

    @doc_inherit(Gate.delete_gates)
    def delete_gates(self, experiment_id, _id=None, gid=None, exclude=None):
        return Gate.delete_gates(self._id, _id, gid, exclude)

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

    def create_complex_population(self, name, base_gate, gates=None):
        """Create a complex population

        Args:
            name (str): Name of the population to create.
            base_gate (str): ID of the gate to build a complex population from.
            gates (str): IDs of other gates to include in the complex population.

        Returns:
            Population: A created complex population.
        """
        return create_complex_population(self._id, name, base_gate, gates)
