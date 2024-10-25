from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple, overload

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pandas.core.frame import DataFrame

import cellengine as ce
from cellengine.resources.attachment import Attachment
from cellengine.resources.compensation import Compensation, UNCOMPENSATED, Compensations
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
from cellengine.utils.helpers import (
    CommentList,
    timestamp_to_datetime,
    datetime_to_timestamp,
)


class Experiment:
    """The main container for an analysis. Don't construct directly; use
    [`Experiment.create`][cellengine.Experiment.create] or
    [`Experiment.get`][cellengine.Experiment.get].

    Not all properties have full support in the Python toolkit. Please open an
    issue if you need to use a property that is not supported.
    """

    def __init__(self, properties: Dict[str, Any]):
        self._properties = properties
        self._changes = set()

    @property
    def _id(self) -> str:
        return self._properties["_id"]

    @property
    def id(self) -> str:
        """Alias for ``_id``."""
        return self._properties["_id"]

    @property
    def name(self) -> str:
        return self._properties["name"]

    @name.setter
    def name(self, name: str):
        self._properties["name"] = name
        self._changes.add("name")

    @property
    def comments(self) -> List[Dict[str, Any]]:
        """Comments for experiment.

        Defaults to overwrite; append new comments with
        experiment.comments.append(dict) with the form:
        ```py
        dict = {
            "insert": "some text",
            "attributes": {"bold": False, "italic": False, "underline": False}
        }
        ```
        """
        return CommentList(self._properties["comments"])

    # TODO this is wrong, it should accept a list of dicts or CommentList
    @comments.setter
    def comments(self, comments: Dict[str, Any]):
        comment = comments.get("insert")
        if comment:
            if comment.endswith("\n") is False:
                comments.update(insert=comment + "\n")
            self._properties["comments"] = comments
            self._changes.add("comments")

    @property
    def created(self) -> datetime:
        created = self._properties["created"]
        return timestamp_to_datetime(created)

    @property
    def deep_updated(self) -> datetime:
        deep_updated = self._properties["deepUpdated"]
        return timestamp_to_datetime(deep_updated)

    @property
    def deleted(self) -> Union[datetime, None]:
        deleted = self._properties["deleted"]
        return timestamp_to_datetime(deleted) if deleted else None

    @deleted.setter
    def deleted(self, deleted: Union[datetime, None]):
        self._properties["deleted"] = (
            datetime_to_timestamp(deleted) if deleted else None
        )
        self._changes.add("deleted")

    @property
    def uploader(self) -> Dict[str, Any]:
        return self._properties["uploader"]

    @property
    def primary_researcher(self) -> Dict[str, Any]:
        """When setting this value, use the user's `_id`."""
        return self._properties["primaryResearcher"]

    @primary_researcher.setter
    def primary_researcher(self, primary_researcher: str):
        self._properties["primaryResearcher"] = primary_researcher
        self._changes.add("primaryResearcher")

    @property
    def path(self) -> List[str]:
        return self._properties["path"]

    @path.setter
    def path(self, path: List[str]):
        self._properties["path"] = path
        self._changes.add("path")

    @property
    def data(self) -> Dict[str, Any]:
        return self._properties["data"]

    @data.setter
    def data(self, data: Dict[str, Any]):
        # TODO how do we detect changes to the dict?
        self._properties["data"] = data
        self._changes.add("data")

    @property
    def data_order(self) -> List[str]:
        return self._properties["dataOrder"]

    @data_order.setter
    def data_order(self, data_order: List[str]):
        # TODO how do we detect changes to the list?
        self._properties["dataOrder"] = data_order
        self._changes.add("dataOrder")

    @property
    def active_compensation(self) -> Union[Compensations, str]:
        return self._properties["activeCompensation"]

    @active_compensation.setter
    def active_compensation(self, active_compensation: Union[Compensations, str]):
        self._properties["activeCompensation"] = active_compensation
        self._changes.add("activeCompensation")

    @property
    def locked(self) -> bool:
        return self._properties["locked"]

    @locked.setter
    def locked(self, locked: bool):
        self._properties["locked"] = locked
        self._changes.add("locked")

    @property
    def retention_policy(self) -> Dict[str, Any]:
        return self._properties["retentionPolicy"]

    # TODO should have something like retain_until(datetime)

    @property
    def clone_source_experiment(self) -> Union[str, None]:
        return self._properties.get("cloneSourceExperiment")

    @property
    def revision_source_experiment(self) -> Union[str, None]:
        return self._properties.get("revisionSourceExperiment")

    @property
    def analysis_source_experiment(self) -> Union[str, None]:
        return self._properties.get("analysisSourceExperiment")

    @property
    def analysis_task(self) -> Union[str, None]:
        return self._properties.get("analysisTask")

    @property
    def revisions(self) -> List[Dict[str, Any]]:
        return self._properties["revisions"]

    @property
    def per_file_compensations_enabled(self) -> bool:
        return self._properties["perFileCompensationsEnabled"]

    @per_file_compensations_enabled.setter
    def per_file_compensations_enabled(self, per_file_compensations_enabled: bool):
        self._properties["perFileCompensationsEnabled"] = per_file_compensations_enabled
        self._changes.add("perFileCompensationsEnabled")

    @property
    def tags(self) -> List[str]:
        return self._properties["tags"]

    @tags.setter
    def tags(self, tags: List[str]):
        # TODO how do we detect changes to the list?
        self._properties["tags"] = tags
        self._changes.add("tags")

    # TODO These are likely being reorganized. Delaying adding to Python API
    # until they are moved or requested by a user.
    #
    # annotation_name_order: List[str]
    # annotation_validators: Dict[str, Any]
    # annotation_sources: Dict[str, Any]
    # annotation_table_sort_columns: List[Union[str, int]]
    # annotation_table_column_widths: Dict[str, float]
    # annotation_table_column_wraps: Dict[str, bool]

    @property
    def sorting_spec(self) -> Dict[str, List[Union[str, None]]]:
        return self._properties["sortingSpec"]

    @sorting_spec.setter
    def sorting_spec(self, sorting_spec: Dict[str, List[Union[str, None]]]):
        self._properties["sortingSpec"] = sorting_spec
        self._changes.add("sortingSpec")

    @property
    def color_spec(self) -> List[Tuple[str, Tuple[Union[str, None], float]]]:
        return self._properties["colorSpec"]

    @color_spec.setter
    def color_spec(self, color_spec: List[Tuple[str, Tuple[Union[str, None], float]]]):
        self._properties["colorSpec"] = color_spec
        self._changes.add("colorSpec")

    @property
    def saved_statistics_exports(self) -> List[Dict[str, Any]]:
        return self._properties["savedStatisticsExports"]

    @saved_statistics_exports.setter
    def saved_statistics_exports(self, saved_statistics_exports: List[Dict[str, Any]]):
        self._properties["savedStatisticsExports"] = saved_statistics_exports
        self._changes.add("savedStatisticsExports")

    @property
    def palettes(self) -> Dict[str, Any]:
        return self._properties["palettes"]

    @palettes.setter
    def palettes(self, palettes: Dict[str, Any]):
        self._properties["palettes"] = palettes
        self._changes.add("palettes")

    # TODO This might be getting removed since deep_updated is what usually
    # matters
    #
    # updated: datetime = field(converter=timestamp_to_datetime)

    @property
    def permissions(self) -> List[Dict[str, Any]]:
        return self._properties["permissions"]

    # TODO set_permissions

    def __repr__(self):
        return f"Experiment(_id='{self._id}', name='{self.name}')"

    @staticmethod
    def get(_id: Optional[str] = None, name: Optional[str] = None) -> Experiment:
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_experiment(**kwargs)

    @staticmethod
    def create(
        name: Optional[str] = None,
        comments: Optional[str] = None,
        uploader: Optional[str] = None,
        primary_researcher: Optional[str] = None,
        tags: List[str] = [],
        path: List[str] = [],
    ) -> Experiment:
        """Creates a new experiment.

        Args:
            name: Defaults to "Untitled Experiment".
            comments: Defaults to None.
            uploader: Defaults to the authenticated user.
            primary_researcher: Defaults to the authenticated user.
            tags: Defaults to empty list.
            path: List of folder IDs comprising the path. Defaults to [] (root).

        Returns:
            The created Experiment.
        """
        experiment_body = {
            k: v
            for (k, v) in {
                "name": name,
                # TODO if we keep the CommentList class, it would probably make
                # sense to use it here.
                "comments": comments,
                "uploader": uploader,
                "primaryResearcher": primary_researcher,
                "tags": tags,
                "path": path,
            }.items()
            if v
        }
        return ce.APIClient().post_experiment(experiment_body)

    def update(self):
        """Save the specified changes to CellEngine and update this instance
        with the new values on success.

        Example:
        ```py
        experiment.name = "New Name"
        experiment.update()
        ```
        """
        update_properties = {key: self._properties[key] for key in self._changes}
        res = ce.APIClient().update_experiment(self._id, update_properties)
        self._properties = res
        self._changes = set()

    def clone(self, props: Dict[str, Any] = {}) -> Experiment:
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
        deleted = datetime.today()
        self.deleted = deleted
        ce.APIClient().update_experiment(self._id, {"deleted": deleted.isoformat()})

    def undelete(self) -> None:
        """Clears a scheduled deletion."""
        if self.deleted:
            self.deleted = None
            ce.APIClient().update_experiment(self._id, {"deleted": self.deleted})

    def save_revision(self, description: str) -> None:
        """
        Saves a revision of the experiment. The new revision will be the last
        entry in the `revisions` property.
        """
        r = ce.APIClient().save_experiment_revision(self._id, description)
        self._properties["revisions"] = r.get("revisions")
        self._properties["deepUpdated"] = r.get("deepUpdated")

    # Attachments

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

    def upload_attachment(
        self, filepath: str, filename: Optional[str] = None
    ) -> Attachment:
        """Upload an attachment to this experiment.

        Args:
            filepath (str): Local path to file to upload.
            filename (str, optional): Optionally, specify a new name for the file.

        Returns:
            The newly uploaded Attachment.
        """
        return ce.APIClient().upload_attachment(self._id, filepath, filename)

    def delete_attachment(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> None:
        """Delete an attachment from this experiment."""
        kwargs = {"name": name} if name else {"_id": _id}
        ce.APIClient().delete_attachment(self._id, **kwargs)

    # Compensations

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

    @overload
    def create_compensation(
        self, name: str, channels: List[str], spill_matrix: List[float]
    ) -> Compensation: ...

    @overload
    def create_compensation(
        self,
        name: str,
        *,
        dataframe: DataFrame,
    ) -> Compensation: ...

    def create_compensation(
        self,
        name: str,
        channels: Optional[List[str]] = None,
        spill_matrix: Optional[List[float]] = None,
        dataframe: Optional[DataFrame] = None,
    ) -> Compensation:
        """Create a new compensation.

        Specify either dataframe or channels and spill_matrix.

        Args:
            name (str): The name of the compensation.
            channels (List[str]): The names of the channels to which this
                compensation matrix applies.
            spill_matrix (List[float]): The row-wise, square spillover matrix.
                The length of the array must be the number of channels squared.
            dataframe (DataFrame): A square pandas DataFrame with channel names
                in [df.index, df.columns].
        """
        return Compensation.create(
            self._id,
            name,
            channels,  # type: ignore
            spill_matrix,  # type: ignore
            dataframe,  # type: ignore
        )

    # FCS Files

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

    def upload_fcs_file(self, filepath, filename: Optional[str] = None):
        """Upload an FCS file to this experiment."""
        return ce.APIClient().upload_fcs_file(self._id, filepath, filename)

    # Gates

    @property
    def gates(self) -> List[Gate]:
        """List all gates on the experiment."""
        return ce.APIClient().get_gates(self._id)

    def get_gate(self, _id: str) -> Gate:
        """Get a specific gate.

        Gates cannot be retrieved by name because all gates in a group of
        tailored gates have the same name, and because compound gates have a
        `names` property instead of a `name` property. Instead, you can filter
        the list of gates as follows to find a simple (not compound) gate:

        ```py
        [g for g in experiment.gates if g.name == "my gate"]
        ```
        """
        return ce.APIClient().get_gate(self._id, _id=_id)

    def create_gates(self, gates: List):
        """Save a collection of gate objects."""
        return Gate.bulk_create(self._id, gates)

    def delete_gate(
        self,
        _id: Optional[str] = None,
        gid: Optional[str] = None,
        exclude: Optional[str] = None,
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
    ) -> Tuple[RectangleGate, Population]: ...

    @overload
    def create_rectangle_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> RectangleGate: ...

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
    ) -> Tuple[PolygonGate, Population]: ...

    @overload
    def create_polygon_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> PolygonGate: ...

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
    ) -> Tuple[EllipseGate, Population]: ...

    @overload
    def create_ellipse_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> EllipseGate: ...

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
    ) -> Tuple[RangeGate, Population]: ...

    @overload
    def create_range_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> RangeGate: ...

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
    ) -> Tuple[QuadrantGate, List[Population]]: ...

    @overload
    def create_quadrant_gate(
        self, *args, create_population: Literal[False], **kwargs
    ) -> QuadrantGate: ...

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

    # Populations

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

    # ScaleSets

    @property
    def scaleset(self) -> ScaleSet:
        """Gets the experiment's ScaleSet"""
        return ce.APIClient().get_scaleset(self._id)

    def get_scaleset(self) -> ScaleSet:
        return self.scaleset

    # Statistics

    def get_statistics(
        self,
        statistics: List[str],
        channels: List[str],
        q: Optional[float] = None,
        annotations: bool = True,
        compensation_id: Union[Compensations, str] = UNCOMPENSATED,
        fcs_file_ids: Optional[List[str]] = None,
        format: Literal["json", "pandas", "TSV", "CSV"] = "pandas",
        layout: Literal["short-wide", "medium", "tall-skinny"] = "medium",
        percent_of: Optional[Union[str, List[str]]] = "PARENT",
        population_ids: List[str] = [],
    ) -> Union[Dict, str, DataFrame]:
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
