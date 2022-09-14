from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple, overload

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from dataclasses_json.cfg import config
from marshmallow import fields
from pandas.core.frame import DataFrame

import cellengine as ce
from cellengine.resources.attachment import Attachment
from cellengine.resources.compensation import Compensation
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.gate import (
    EllipseGate,
    Gate,
    PolygonGate,
    QuadrantGate,
    RangeGate,
    RectangleGate,
    SplitGate,
)
from cellengine.resources.population import Population
from cellengine.resources.scaleset import ScaleSet
from cellengine.utils.dataclass_mixin import DataClassMixin, ReadOnly
from cellengine.utils.helpers import (
    CommentList,
    datetime_to_timestamp,
    is_valid_id,
    timestamp_to_datetime,
)


@dataclass
class Experiment(DataClassMixin):
    """The main container for an analysis. Don't construct directly; use
    [`Experiment.create`][cellengine.Experiment.create] or
    [`Experiment.get`][cellengine.Experiment.get]."""

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

    def clone(self, props: Optional[Dict[str, Any]] = None) -> Experiment:
        """
        Saves a deep copy of the experiment and all of its resources, including
        attachments, FCS files, gates and populations.

        Args:
            props (Dict[str, Any]): Optional keys are:
                name (str): The name to give the new experiment. Defaults to
                    "[Original Experiment]-1"
                path (List[str]): Array of folder IDs comprising the path.

        Returns:
            Experiment: A deep copy of the experiment.
        """
        return ce.APIClient().clone_experiment(self._id, props)

    def delete(self) -> None:
        """Marks the experiment as deleted.

        Deleted experiments are permanently deleted after approximately
        7 days. Until then, deleted experiments can be recovered.
        """
        self.deleted = datetime.today()

    def undelete(self) -> None:
        """Clear a scheduled deletion."""
        if self.deleted:
            del self.deleted

    @property
    def active_compensation(self) -> Optional[Union[str, int]]:
        """The most recently used compensation.

        Accepted values are:

        - A Compensation object (value will be set to its `_id`)
        - A Compensation ID
        - A `cellengine` Compensation constant:
          [`UNCOMPENSATED`][cellengine.UNCOMPENSATED],
          [`FILE_INTERNAL`][cellengine.FILE_INTERNAL] or
          [`PER_FILE`][cellengine.PER_FILE].

        Example:
        ```python
        import cellengine
        exp = cellengine.get_experiment(name='my experiment')
        experiment.active_compensation = cellengine.UNCOMPENSATED
        ```
        """
        return self._active_comp

    @active_compensation.setter
    def active_compensation(self, compensation: Union[Compensation, int, str]):
        if isinstance(compensation, Compensation):
            self._active_comp = compensation._id
        elif isinstance(compensation, str) and is_valid_id(compensation):
            self._active_comp = compensation
        elif isinstance(compensation, int) and compensation in [
            ce.UNCOMPENSATED,
            ce.PER_FILE,
            ce.FILE_INTERNAL,
        ]:
            self._active_comp = compensation
        else:
            raise ValueError(
                f"Value '{compensation}' can not be set as the active compensation."
            )

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

    def get_gate(self, _id: Optional[str] = None, name: Optional[str] = None) -> Gate:
        """Get a specific gate."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_gate(self._id, **kwargs)

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
    ) -> Union[Dict, str, DataFrame]:
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
        """Gets the experiment's ScaleSet"""
        return ce.APIClient().get_scaleset(self._id)

    def get_scaleset(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> ScaleSet:
        """Get a specific scaleset."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_scaleset(self._id, **kwargs)

    def create_gates(self, gates: List):
        """Save a collection of gate objects."""
        return Gate.bulk_create(self._id, gates)

    def delete_gate(
        self, _id: str = None, gid: str = None, exclude: str = None
    ) -> None:
        """Delete a gate or gate family.
        See the
        [`APIClient`][cellengine.utils.api_client.APIClient.APIClient.delete_gate]
        for more information.
        """
        return ce.APIClient().delete_gate(self._id, _id, gid, exclude)

    def delete_gates(self, ids: List[str]) -> None:
        """Deletes multiple gates provided a list of _ids."""
        ce.APIClient().delete_gates(self._id, ids)

    @overload
    def create_rectangle_gate(
        self, *args, create_population: Literal[True], **kwargs
    ) -> Tuple[RectangleGate, Population]:
        ...

    @overload
    def create_rectangle_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> RectangleGate:
        ...

    def create_rectangle_gate(
        self, *args, create_population: bool = True, **kwargs
    ) -> Union[RectangleGate, Tuple[RectangleGate, Population]]:
        """Create a RectangleGate.

        Accepts all args and kwargs available for
        [`RectangleGate.create()`][cellengine.resources.gate.RectangleGate.create].
        """
        return RectangleGate.create(
            self._id,
            *args,
            create_population=create_population,  # type: ignore pyright limitation
            **kwargs,
        )

    @overload
    def create_polygon_gate(
        self, *args, create_population: Literal[True], **kwargs
    ) -> Tuple[PolygonGate, Population]:
        ...

    @overload
    def create_polygon_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> PolygonGate:
        ...

    def create_polygon_gate(
        self, *args, create_population: bool = True, **kwargs
    ) -> Union[PolygonGate, Tuple[PolygonGate, Population]]:
        """Create a PolygonGate.

        Accepts all args and kwargs available for
        [`PolygonGate.create()`][cellengine.resources.gate.PolygonGate.create].
        """
        return PolygonGate.create(
            self._id,
            *args,
            create_population=create_population,  # type: ignore pyright limitation
            **kwargs,
        )

    @overload
    def create_ellipse_gate(
        self, *args, create_population: Literal[True], **kwargs
    ) -> Tuple[EllipseGate, Population]:
        ...

    @overload
    def create_ellipse_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> EllipseGate:
        ...

    def create_ellipse_gate(
        self, *args, create_population: bool = True, **kwargs
    ) -> Union[EllipseGate, Tuple[EllipseGate, Population]]:
        """Create an EllipseGate.

        Accepts all args and kwargs available for
        [`EllipseGate.create()`][cellengine.resources.gate.EllipseGate.create].
        """
        return EllipseGate.create(
            self._id,
            *args,
            create_population=create_population,  # type: ignore pyright limitation
            **kwargs,
        )

    @overload
    def create_range_gate(
        self, *args, create_population: Literal[True], **kwargs
    ) -> Tuple[RangeGate, Population]:
        ...

    @overload
    def create_range_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> RangeGate:
        ...

    def create_range_gate(
        self, *args, create_population: bool = True, **kwargs
    ) -> Union[RangeGate, Tuple[RangeGate, Population]]:
        """Create a RangeGate.

        Accepts all args and kwargs available for
        [`RangeGate.create()`][cellengine.resources.gate.RangeGate.create].
        """
        return RangeGate.create(
            self._id,
            *args,
            create_population=create_population,  # type: ignore pyright limitation
            **kwargs,
        )

    def create_split_gate(
        self, *args, create_population: bool = True, **kwargs
    ) -> SplitGate:
        """Create a SplitGate.

        Accepts all args and kwargs available for
        [`SplitGate.create()`][cellengine.resources.gate.SplitGate.create].
        """
        return SplitGate.create(
            self._id,
            *args,
            create_population=create_population,  # type: ignore pyright limitation
            **kwargs,
        )

    @overload
    def create_quadrant_gate(
        self, *args, create_population: Literal[True], **kwargs
    ) -> Tuple[QuadrantGate, List[Population]]:
        ...

    @overload
    def create_quadrant_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> QuadrantGate:
        ...

    def create_quadrant_gate(
        self, *args, create_population: bool = True, **kwargs
    ) -> Union[QuadrantGate, Tuple[QuadrantGate, List[Population]]]:
        """Create a QuadrantGate.

        Accepts all args and kwargs available for
        [`QuadrantGate.create()`][cellengine.resources.gate.QuadrantGate.create].
        """
        return QuadrantGate.create(
            self._id,
            *args,
            create_population=create_population,  # type: ignore pyright limitation
            **kwargs,
        )

    def create_population(self, population: Dict) -> Population:
        """Create a population.

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
