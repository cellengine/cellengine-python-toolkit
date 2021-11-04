from __future__ import annotations
from datetime import datetime

from marshmallow import fields

from cellengine.utils.dataclass_mixin import DataClassMixin, ReadOnly
from dataclasses import dataclass, field
from custom_inherit import doc_inherit
from typing import Any, Optional, Dict, Union, List

from dataclasses_json.cfg import config

import cellengine as ce
from cellengine.resources.population import Population
from cellengine.resources.scaleset import ScaleSet
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.compensation import Compensation
from cellengine.resources.attachment import Attachment
from cellengine.resources.gates import (
    Gate,
    RectangleGate,
    PolygonGate,
    RangeGate,
    SplitGate,
    EllipseGate,
    QuadrantGate,
)
from cellengine.utils.helpers import (
    CommentList,
    datetime_to_timestamp,
    timestamp_to_datetime,
)


def _strip_experiment_id(*args):
    if len(args[0]) < 1:
        return
    lines = args[0].split("\n")
    lines.pop(lines.index([l for l in lines if "experiment_id (str)" in l][0]))
    return "\n".join(lines)


@dataclass
class Experiment(DataClassMixin):

    name: str
    annotation_validators: Dict[Any, Any]
    annotation_name_order: List[str]
    annotation_table_sort_columns: List[Union[str, int]]
    _comments: List[Dict[str, Any]] = field(metadata=config(field_name="comments"))
    primary_researcher: Dict[str, Any]
    sorting_spec: Dict[Any, Any]
    tags: List[str]
    created: datetime = field(
        metadata=config(
            encoder=datetime_to_timestamp,
            decoder=timestamp_to_datetime,
            mm_field=fields.DateTime(),
        ),
        default=ReadOnly(),
    )  # type: ignore
    updated: datetime = field(
        metadata=config(
            encoder=datetime_to_timestamp,
            decoder=timestamp_to_datetime,
            mm_field=fields.DateTime(),
        ),
        default=ReadOnly(),
    )  # type: ignore
    _active_comp: Optional[Union[int, str]] = field(
        default=None, metadata=config(field_name="activeCompensation")
    )
    data: Optional[Dict[Any, Any]] = field(default=None)
    deleted: Optional[datetime] = field(
        default=None,
        metadata=config(
            encoder=lambda t: datetime_to_timestamp(t) if t else t,
            decoder=lambda t: timestamp_to_datetime(t) if t else t,
            mm_field=fields.DateTime(),
        ),
    )
    deep_updated: datetime = field(
        metadata=config(
            encoder=datetime_to_timestamp,
            decoder=timestamp_to_datetime,
            mm_field=fields.DateTime(),
        ),
        default=ReadOnly(optional=True),
    )  # type: ignore
    analysis_source_experiment: Optional[str] = field(
        default=ReadOnly(optional=True)
    )  # type: ignore
    clone_source_experiment: Optional[str] = field(
        default=ReadOnly(optional=True)
    )  # type: ignore
    locked: bool = field(default=ReadOnly())  # type: ignore
    permissions: List[Dict[Any, Any]] = field(default=ReadOnly())  # type: ignore
    per_file_compensations_enabled: Optional[bool] = field(default=None)
    retention_policy: Dict[str, Any] = field(default=ReadOnly())  # type: ignore
    revision_source_experiment: Optional[str] = field(
        default=ReadOnly(optional=True)
    )  # type: ignore
    _id: str = field(
        metadata=config(field_name="_id"), default=ReadOnly()
    )  # type: ignore
    revisions: List[Dict[str, Any]] = field(default=ReadOnly())  # type: ignore
    uploader: Dict[str, Any] = field(default=ReadOnly())  # type: ignore

    def __repr__(self):
        return f"Experiment(_id='{self._id}', name='{self.name}')"

    @property
    def client(self):
        return ce.APIClient()

    @property
    def comments(self):
        """Get comments for experiment.

        Defaults to overwrite; append new comments with
        experiment.comments.append(dict) with the form:
        dict = {"insert": "some text",
        "attributes": {"bold": False, "italic": False, "underline": False}}.
        """
        comments = self._comments
        if type(comments) is not CommentList:
            self._comments = CommentList(comments)
        return comments

    @comments.setter
    def comments(self, comments: Dict[str, Any]):
        comment = comments.get("insert")
        if comment:
            if comment.endswith("\n") is False:
                comments.update(insert=comment + "\n")
            self._comments = comments  # type: ignore

    @staticmethod
    def get(_id: str = None, name: str = None) -> Experiment:
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_experiment(**kwargs)

    @staticmethod
    def create(
        name: str = None,
        comments: str = None,
        uploader: str = None,
        primary_researcher: str = None,
        tags: List[str] = None,
    ) -> Union[Experiment, Dict]:
        """Post a new experiment to CellEngine.

        Args:
            name: Defaults to "Untitled Experiment".
            comments: Defaults to None.
            uploader: Defaults to user making request.
            primary_researcher: Defaults to user making request.
            tags: Defaults to empty list.

        Returns:
            Creates the Experiment in CellEngine and returns it.
        """
        experiment_body = {
            k: v
            for (k, v) in {
                "name": name,
                "comments": comments,
                "uploader": uploader,
                "primaryResearcher": primary_researcher,
                "tags": tags,
            }.items()
            if v
        }
        return ce.APIClient().post_experiment(experiment_body)

    def update(self):
        """Save changes to this Experiment to CellEngine."""
        res = ce.APIClient().update_experiment(self._id, self.to_dict())
        self.__dict__.update(Experiment.from_dict(res).__dict__)

    def clone(self, name: str = None):
        """
        Saves a deep copy of the experiment and all of its resources, including
        attachments, FCS files, gates and populations.

        Args:
            name: The name to give the new experiment. Defaults to
                "[Original Experiment]-1"

        Returns:
            Experiment: A deep copy of the experiment.
        """
        return ce.APIClient().clone_experiment(self._id, name=name)

    @property
    def delete(self):
        """Marks the experiment as deleted.

        Deleted experiments are permanently deleted after approximately
        7 days. Until then, deleted experiments can be recovered.
        """
        self.deleted = datetime.today()

    @property
    def undelete(self):
        """Clear a scheduled deletion."""
        if self.deleted:
            del self.deleted

    @property
    def active_compensation(self) -> Optional[Union[Compensation, int]]:
        active_comp = self._active_comp
        if type(active_comp) is str:
            return ce.APIClient().get_compensation(self._id, active_comp)
        elif type(active_comp) is int:
            return active_comp
        elif active_comp is None:
            return None
        raise ValueError(
            f"Value '{active_comp}' is not a valid for activeCompensation."
        )

    @active_compensation.setter
    def active_compensation(self, compensation: Union[Compensation, int]):
        if type(compensation) is Compensation:
            self._active_comp = compensation._id  # type: ignore
        elif (
            compensation == "UNCOMPENSATED"
            or compensation == "FILE_INTERNAL"
            or compensation == "PER_FILE"
        ):
            self._active_comp = compensation  # type: ignore

    @property
    def attachments(self) -> List[Attachment]:
        """List all attachments on the experiment."""
        return ce.APIClient().get_attachments(self._id)

    def get_attachment(self, _id: Optional[str] = None, name: Optional[str] = None):
        return ce.APIClient().get_attachment(self._id, _id, name)

    def download_attachment(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> bytes:
        """Get a specific attachment."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().download_attachment(self._id, **kwargs)

    def upload_attachment(self, filepath: str, filename: str = None):
        """Upload an attachment to this experiment."""
        ce.APIClient().upload_attachment(self._id, filepath, filename)

    @property
    def compensations(self) -> List[Compensation]:
        """List all compensations on the experiment."""
        return ce.APIClient().get_compensations(self._id)

    def get_compensation(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> Compensation:
        """Get a specific compensation."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_compensation(self._id, **kwargs)

    def create_compensation(
        self, name: str, channels: List[str], spill_matrix: List[float]
    ):
        """Create a new compensation to this experiment

        Args:
            name (str): The name of the compensation.
            channels (List[str]): The names of the channels to which this
                compensation matrix applies.
            spill_matrix (List[float]): The row-wise, square spillover matrix. The
                length of the array must be the number of channels squared.
        """
        body = {"name": name, "channels": channels, "spillMatrix": spill_matrix}
        ce.APIClient().post_compensation(self._id, body)

    @property
    def fcs_files(self) -> List[FcsFile]:
        """List all FCS files on the experiment."""
        return ce.APIClient().get_fcs_files(self._id)

    def get_fcs_file(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> FcsFile:
        """Get a specific FCS file."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_fcs_file(self._id, **kwargs)

    def upload_fcs_file(self, filepath, filename: str = None):
        """Upload an FCS file to this experiment."""
        ce.APIClient().upload_fcs_file(self._id, filepath, filename)

    @property
    def gates(self) -> List[Gate]:
        """List all gates on the experiment."""
        return ce.APIClient().get_gates(self._id)

    def get_gate(self, _id: str) -> Gate:
        """Get a specific gate by _id."""
        return ce.APIClient().get_gate(self._id, _id)

    @property
    def populations(self) -> List[Population]:
        """List all populations in the experiment."""
        return ce.APIClient().get_populations(self._id)

    def get_population(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> Population:
        """Get a specific population."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_population(self._id, **kwargs)

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
        """
        Request Statistics from CellEngine.

        Args:
            statistics: Statistical method to request. Any of "mean", "median",
                "quantile", "mad" (median absolute deviation), "geometricmean",
                "eventcount", "cv", "stddev" or "percent" (case-insensitive).
            q (int): quantile (required for "quantile" statistic)
            channels (Union[str, List[str]]): for "mean", "median", "geometricMean",
                "cv", "stddev", "mad" or "quantile" statistics. Names of channels
                to calculate statistics for.
            annotations: Include file annotations in output
                (defaults to False).
            compensation_id: Compensation to use for gating and
                statistic calculation.
                Defaults to uncompensated. Three special constants may be used:
                    0: Uncompensated
                    -1: File-Internal Compensation Uses the file's internal
                        compensation matrix, if available. If not, an error
                        will be returned.
                    -2: Per-File Compensation Use the compensation assigned to
                        each individual FCS file.
            fcs_file_ids: FCS files to get statistics for. If
                omitted, statistics for all non-control FCS files will be returned.
            format: str: One of "TSV (with[out] header)",
                "CSV (with[out] header)" or "json" (default), "pandas",
                case-insensitive.
            layout: str: The file (TSV/CSV) or object (JSON) layout.
                One of "tall-skinny", "medium", or "short-wide".
            percent_of: str or List[str]: Population ID or array of
                population IDs.  If omitted or the string "PARENT", will calculate
                percent of parent for each population. If a single ID, will calculate
                percent of that population for all populations specified by
                population_ids. If a list, will calculate percent of each of
                those populations.
            population_ids: List[str]: List of population IDs.
                Defaults to ungated.
        Returns:
            statistics: Dict, String, or pandas.Dataframe
        """
        return ce.APIClient().get_statistics(
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

    @property
    def scalesets(self) -> ScaleSet:
        """List all scalesets in the experiment."""
        return ce.APIClient().get_scaleset(self._id)

    def get_scaleset(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> ScaleSet:
        """Get a specific scaleset."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_scaleset(self._id, **kwargs)

    def create_gates(self, gates: List[Gate]):
        """Save a collection of gate objects. Does not create populations."""
        return self.client.create(gates)

    def delete_gate(
        self, _id: str = None, gid: str = None, exclude: str = None
    ) -> None:
        """Delete a gate or gate family.
        See the
        [`APIClient`][cellengine.utils.api_client.APIClient.APIClient.delete_gate]
        for more information.
        """
        return ce.APIClient().delete_gate(self._id, _id, gid, exclude)

    @doc_inherit(RectangleGate.create, style=_strip_experiment_id)
    def create_rectangle_gate(self, *args, **kwargs):
        gate = RectangleGate.create(self._id, *args, **kwargs)
        gate.update()
        return gate

    @doc_inherit(PolygonGate.create, style=_strip_experiment_id)
    def create_polygon_gate(self, *args, **kwargs):
        gate = PolygonGate.create(self._id, *args, **kwargs)
        gate.update()
        return gate

    @doc_inherit(EllipseGate.create, style=_strip_experiment_id)
    def create_ellipse_gate(self, *args, **kwargs):
        gate = EllipseGate.create(self._id, *args, **kwargs)
        gate.update()
        return gate

    @doc_inherit(RangeGate.create, style=_strip_experiment_id)
    def create_range_gate(self, *args, **kwargs):
        gate = RangeGate.create(self._id, *args, **kwargs)
        gate.update()
        return gate

    @doc_inherit(SplitGate.create, style=_strip_experiment_id)
    def create_split_gate(self, *args, **kwargs):
        gate = SplitGate.create(self._id, *args, **kwargs)
        gate.update()
        return gate

    @doc_inherit(QuadrantGate.create, style=_strip_experiment_id)
    def create_quadrant_gate(self, *args, **kwargs):
        gate = QuadrantGate.create(self._id, *args, **kwargs)
        gate.update()
        return gate

    def create_population(self, population: Dict) -> Population:
        """Create a complex population

        Args:
            population (dict): The population to create.
                Use the `ComplexPopulationBuilder` to construct a complex population.

        Examples:
            ```py
            experiment.create_population({
                "name": name,
                "terminalGateGid": GID,
                "parentId": parent._id,
                "gates": json.dumps({"$and": AND_GATES})
            })
            ```

        Returns:
            The new population.
        """
        return ce.APIClient().post_population(self._id, population)
