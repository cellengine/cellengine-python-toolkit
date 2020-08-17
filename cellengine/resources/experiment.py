from custom_inherit import doc_inherit
from typing import Optional, Dict, Union, List
import fcsparser

import cellengine as ce
from cellengine.payloads.experiment import _Experiment
from cellengine.utils.complex_population_builder import ComplexPopulationBuilder
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
    @staticmethod
    def get(_id: str = None, name: str = None):
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_experiment(**kwargs)

    @staticmethod
    def create(
        name: str = None,
        comments: str = None,
        uploader: str = None,
        primary_researcher: str = None,
        public: bool = False,
        tags: List[str] = None,
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
            k: v
            for (k, v) in {
                "name": name,
                "comments": comments,
                "uploader": uploader,
                "primaryResearcher": primary_researcher,
                "public": public,
                "tags": tags,
            }.items()
            if v
        }
        return ce.APIClient().post_experiment(experiment_body)

    def update(self, inplace: bool = True):
        """Save changes to this Experiment to CellEngine.

        Args:
            inplace (bool): Update this entity or return a new one.

        Returns:
            Experiment or None: If inplace is True, returns a new Experiment.
            Otherwise, updates the current experiment.
        """
        res = ce.APIClient().update_experiment(self._id, self._properties)
        if inplace:
            self._properties.update(res)
        else:
            return self.__class__(res)

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

    @property
    def active_compensation(self) -> Compensation:
        active_comp = self._properties["activeCompensation"]
        return ce.APIClient().get_compensation(active_comp) if active_comp else None

    @active_compensation.setter
    def active_compensation(self, compensation: str):
        self._properties["activeCompensation"] = compensation
        self.update()

    @property
    def attachments(self) -> List[Attachment]:
        """List all attachments on the experiment."""
        return ce.APIClient().get_attachments(self._id)

    def get_attachment(self, _id: Optional[str] = None, name: Optional[str] = None):
        return ce.APIClient().get_attachment(self._id, _id, name)

    def download_attachment(
        self, _id: Optional[str] = None, name: Optional[str] = None
    ) -> Attachment:
        """Get a specific attachment."""
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().download_attachment(self._id, **kwargs)

    def post_attachment(self, filepath: str, filename: str = None):
        """Upload an attachment to this experiment."""
        ce.APIClient().post_attachment(self._id, filepath, filename)

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

    def post_compensation(
        self, name: str, channels: List[str], spill_matrix: List[float]
    ):
        """Post a new compensation to this experiment

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

    @doc_inherit(Gate.delete_gates)
    def delete_gates(self, _id=None, gid=None, exclude=None):
        return ce.APIClient().delete_gate(self._id, _id, gid, exclude)

    @doc_inherit(format_rectangle_gate)
    def create_rectangle_gate(self, *args, **kwargs):
        post_body = format_rectangle_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    @doc_inherit(format_polygon_gate)
    def create_polygon_gate(self, *args, **kwargs):
        post_body = format_polygon_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    @doc_inherit(format_ellipse_gate)
    def create_ellipse_gate(self, *args, **kwargs):
        post_body = format_ellipse_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    @doc_inherit(format_range_gate)
    def create_range_gate(self, *args, **kwargs):
        post_body = format_range_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    @doc_inherit(format_split_gate)
    def create_split_gate(self, *args, **kwargs):
        post_body = format_split_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    @doc_inherit(format_quadrant_gate)
    def create_quadrant_gate(self, *args, **kwargs):
        post_body = format_quadrant_gate(self._id, *args, **kwargs)
        return ce.APIClient().post_gate(self._id, post_body)

    def create_population(self, population: Dict):
        """Create a complex population

        Args:
            population (dict): The population to create. Use the
                `ComplexPopulationBuilder` to construct a complex population.

        Returns:
            Population: A created complex population.
        """
        raise NotImplementedError(
            """
            This method has not been implemented yet.
            Several CellEngine features, such as deletion
            of complex populations, are currently
            unavailable.
            """
        )
        return ce.APIClient().post_population(self._id, population)
