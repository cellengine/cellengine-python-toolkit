from custom_inherit import doc_inherit
from typing import Optional, Dict, Union, List

import cellengine as ce
from cellengine.payloads.experiment import _Experiment
from cellengine.utils.complex_population_creator import create_complex_population
from cellengine.resources.population import Population
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.compensation import Compensation
from cellengine.resources.attachment import Attachment
from cellengine.resources.gate import Gate
from cellengine.payloads.gate_utils import (
    format_rectangle_gate,
    format_polygon_gate,
    format_ellipse_gate,
    format_range_gate,
    format_split_gate,
    format_quadrant_gate,
)
from cellengine.utils.helpers import (
    GetSet,
    today_timestamp,
)


class Experiment(_Experiment):
    @classmethod
    def get(cls, _id: str, name: str = None):
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_experiment(**kwargs)

    @classmethod
    def create(
        cls,
        name: str = None,
        comments: str = None,
        uploader: str = None,
        primary_researcher: str = None,
        public: bool = False,
        tags: List[str] = None,
        as_dict=False,
    ):
        """Post a new experiment to CellEngine.

        Args:
            name: Defaults to "Untitled Experiment".
            comments: Defaults to None.
            uploader: Defaults to user making request.
            primary_researcher: Defaults to user making request.
            public: Defaults to false.
            tags: Defaults to empty list.
            as_dict: Whether to return the experiment as an Experiment object or a dict.

        Returns:
            Experiment: Creates the Experiment on CellEngine and returns it.
        """
        experiment_body = {
            "name": name,
            "comments": comments,
            "uploader": uploader,
            "primaryResearcher": primary_researcher,
            "public": public,
            "tags": tags,
        }
        return ce.APIClient().post_experiment(experiment_body, as_dict=as_dict)

    def update(self):
        """Save changes to this Experiment object to CellEngine.

        Returns:
            None: Updates the Experiment on CellEngine and then
                  synchronizes the properties with the current Experiment object.

        """
        res = ce.APIClient().update_experiment(self._id, self._properties)
        self._properties.update(res)

    def clone(self, name=None):
        """
        Saves a deep copy of the experiment and all of its resources, including
        attachments, FCS files, gates and populations.

        Args:
            name: The name to give the new experiment. Defaults to "[Original Experiment]-1"
            as_dict: Optionally return the new experiment as a dict.

        Returns:
            A deep copy of the experiment.
        """
        return ce.APIClient().clone_experiment(self._id, name=name)

    @property
    def delete(self, confirm=False):
        """Marks the experiment as deleted.

        Deleted experiments are permanently deleted after approximately
        7 days. Until then, deleted experiments can be recovered.
        """
        if confirm:
            self._properties["deleted"] = today_timestamp()

    @property
    def undelete(self):
        """Remove a scheduled deletion."""
        if self._properties.get("deleted") is not None:
            self._properties["delete"] = None

    # TODO: make this override _Experimen to return a compensation
    active_compensation = GetSet("activeCompensation")

    @property
    def attachments(self) -> List[Attachment]:
        """List all attachments on the experiment."""
        return ce.APIClient().get_attachments(self._id)

    def get_attachment(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> Attachment:
        """Get a specific attachment."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_attachment(self._id, **kwargs)

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

    @property
    def fcs_files(self) -> List[FcsFile]:
        """List all files on the experiment."""
        return ce.APIClient().get_fcs_files(self._id)

    def get_fcs_file(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> FcsFile:
        """Get a specific fcs_file."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_fcs_file(self._id, **kwargs)

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
    ):
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

    # Gate Methods:

    # @doc_inherit(_Gate.delete_gates)
    def delete_gates(self, experiment_id, _id=None, gid=None, exclude=None):
        raise NotImplementedError
        # return _Gate.delete_gates(self._id, _id, gid, exclude)

    # @doc_inherit(_RectangleGate.create)
    def create_rectangle_gate(self, *args, **kwargs):
        post_body = format_rectangle_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    # @doc_inherit(_PolygonGate.create)
    def create_polygon_gate(self, *args, **kwargs):
        post_body = format_polygon_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    # @doc_inherit(_EllipseGate.create)
    def create_ellipse_gate(self, *args, **kwargs):
        post_body = format_ellipse_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    # @doc_inherit(_RangeGate.create)
    def create_range_gate(self, *args, **kwargs):
        post_body = format_range_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    # @doc_inherit(_SplitGate.create)
    def create_split_gate(self, *args, **kwargs):
        post_body = format_split_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    # @doc_inherit(_QuadrantGate.create)
    def create_quadrant_gate(self, *args, **kwargs):
        post_body = format_quadrant_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    def create_complex_population(self, name, base_gate, gates=None):
        """Create a complex population

        Args:
            name (str): Name of the population to create.
            base_gate (str): ID of the gate to build a complex population from.
            gates (str): IDs of other gates to include in the complex population.

        Returns:
            Population: A created complex population.
        """
        raise NotImplementedError
        # return create_complex_population(self._id, name, base_gate, gates)
