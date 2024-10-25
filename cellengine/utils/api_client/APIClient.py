from __future__ import annotations
from cellengine.utils.types import ApplyTailoringRes
from functools import lru_cache
from getpass import getpass
import importlib
import json
import os
from warnings import warn
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union
from io import BytesIO

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import pandas
from pandas.core.frame import DataFrame
from requests_toolbelt.multipart.encoder import MultipartEncoder

from cellengine.utils.api_client.APIError import APIError
from cellengine.utils.api_client.BaseAPIClient import BaseAPIClient
from cellengine.utils.singleton import Singleton

from ...resources.attachment import Attachment
from ...resources.compensation import Compensation, Compensations, UNCOMPENSATED
from ...resources.experiment import Experiment, ImportOpts
from ...resources.fcs_file import FcsFile
from ...resources.folder import Folder
from ...resources.gate import (
    EllipseGate,
    Gate,
    PolygonGate,
    QuadrantGate,
    RangeGate,
    RectangleGate,
    SplitGate,
)
from ...resources.plot import Plot
from ...resources.population import Population
from ...resources.scaleset import ScaleSet


CE = TypeVar(
    "CE",
    Attachment,
    Compensation,
    Experiment,
    FcsFile,
    Folder,
    Gate,
    Plot,
    Population,
    ScaleSet,
)

_Gate = TypeVar(
    "_Gate",
    Gate,
    RectangleGate,
    EllipseGate,
    PolygonGate,
    RangeGate,
    QuadrantGate,
    SplitGate,
)


class APIClient(BaseAPIClient, metaclass=Singleton):
    _API_NAME = "CellEngine Python Toolkit"

    def __init__(self, username=None, password=None, token=None):
        super(APIClient, self).__init__()
        self.base_url = os.environ.get("CELLENGINE_BASE_URL", "https://cellengine.com")
        self.username = username or os.environ.get("CELLENGINE_USERNAME")
        self.password = password or os.environ.get("CELLENGINE_PASSWORD")
        self.token = token or os.environ.get("CELLENGINE_AUTH_TOKEN")
        self.user_id = None
        self.authenticated = self._authenticate(
            self.username, self.password, self.token
        )

        self.cache_info = self._get_id_by_name.cache_info
        self.cache_clear = self._get_id_by_name.cache_clear

    def __repr__(self):
        if self.username:
            return f"Client(user={self.username})"
        else:
            return "Client(TOKEN)"

    def _authenticate(
        self, username: Optional[str], password: Optional[str], token: Optional[str]
    ):
        """Authenticate with the CellEngine API.

        There are two ways of authenticating:
            1. Username and password. Use this to authenticate a user in a
               dynamic session.
            1. API token. This is the preferred method for unattended
               applications (such as LIMS integrations) because it allows a
               limited set of permissions to be granted to the application.

        Args:
            username: Login credential set during CellEngine registration
            password: Password for login
            token: Authentication token; may be passed instead of username and password
        """
        if username:
            self.username = username
            self.password = password or getpass()

            try:
                res = self._post(
                    f"{self.base_url}/api/v1/signin",
                    {"username": self.username, "password": self.password},
                )
            except APIError as err:
                if '"otp" is required' in err.message:
                    otp = input("One-time code: ")
                    res = self._post(
                        f"{self.base_url}/api/v1/signin",
                        {
                            "username": self.username,
                            "password": self.password,
                            "otp": otp,
                        },
                    )
                else:
                    raise err

            self.token = res["token"]
            os.environ["CELLENGINE_AUTH_TOKEN"] = self.token
            self.user_id = res["userId"]

        elif token:
            self.requests_session.cookies.update({"token": "{0}".format(token)})

        else:
            raise RuntimeError(
                "Authentication failed: Username or token must be provided."
            )
        return True

    def _get_by_name(
        self, name: str, resource_type: str, experiment_id: Optional[str] = None
    ) -> Any:
        if resource_type == "experiments":
            path = "experiments"
        elif resource_type == "folders":
            path = "folders"
        else:
            path = f"experiments/{experiment_id}/{resource_type}"

        if (resource_type == "fcsfiles") or (resource_type == "attachments"):
            query = "filename"
        else:
            query = "name"

        params = {"query": f'and(eq({query},"{name}"),eq(deleted,null))', "limit": 2}
        res = self._get(f"{self.base_url}/api/v1/{path}", params=params)

        if type(res) is not list:
            raise RuntimeError("Unexpected non-list response.")

        if len(res) == 0:
            raise RuntimeError(f"Resource with the name '{name}' does not exist.")
        elif len(res) > 1:
            raise RuntimeError(f"More than one resource with the name '{name}' exists.")
        return res[0]

    @lru_cache(maxsize=None)
    def _get_id_by_name(self, name, resource_type, experiment_id):
        if resource_type != "experiments":
            path = f"experiments/{experiment_id}/{resource_type}"
        else:
            path = "experiments"
        if (resource_type == "fcsfiles") or (resource_type == "attachments"):
            query = "filename"
        else:
            query = "name"
        res = self._lookup_by_name(path, query, name)
        try:
            return self._handle_response(res)["_id"]
        except RuntimeError as e:
            raise RuntimeError(str(e).format(name))

    def _lookup_by_name(self, path, query, name):
        params = {"query": f'and(eq({query},"{name}"),eq(deleted,null))', "limit": 2}
        return self._get(f"{self.base_url}/api/v1/{path}", params=params)

    def _handle_response(self, response):
        if type(response) is list:
            self._handle_list(response)
        else:
            response = [response]
        return response[0]

    def _handle_list(self, response: List) -> None:
        # FIXME these are supposed to be f-strings
        if len(response) == 0:
            raise RuntimeError("Resource with the name '{}' does not exist.")
        elif len(response) > 1:
            raise RuntimeError("More than one resource with the name '{}' exists.")

    def update_entity(self, experiment_id, _id, entity_type, body) -> dict:
        return self._patch(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/{entity_type}/{_id}",
            json=body,
        )

    def delete_entity(self, experiment_id, entity_type, _id):
        url = f"{self.base_url}/api/v1/experiments/{experiment_id}/{entity_type}/{_id}"
        self._delete(url)

    # ------------------------------ Attachments -------------------------------

    def get_attachments(self, experiment_id) -> List[Attachment]:
        attachments = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/attachments"
        )
        return [Attachment(attachment) for attachment in attachments]

    def download_attachment(self, experiment_id, _id=None, name=None) -> bytes:
        """Download an attachment"""
        _id = _id or self._get_id_by_name(name, "attachments", experiment_id)
        attachment = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/attachments/{_id}",
            raw=True,
        )
        return attachment

    def get_attachment(
        self,
        experiment_id: str,
        _id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Attachment:
        if _id is None and name is None:
            raise RuntimeError("Either _id or name must be specified.")
        if _id is not None and name is not None:
            raise RuntimeError("Only one of _id or name may be specified.")
        # Attachments are somewhat unusual in the CellEngine API: the GET route
        # can currently only return the file content, not the metadata, so we
        # have to list attachments.
        if name is not None:
            attachment = self._get_by_name(name, "attachments", experiment_id)
        else:  # _id is not None
            params = {"query": f'eq(_id,"{_id}")'}
            attachments = self._get(
                f"{self.base_url}/api/v1/experiments/{experiment_id}/attachments",
                params=params,
            )
            if len(attachments) == 0:
                raise RuntimeError(f"Attachment with ID {_id} not found.")
            attachment = attachments[0]
        return Attachment(attachment)

    def upload_attachment(
        self, experiment_id, filepath: str, filename: Optional[str] = None
    ) -> Attachment:
        """Upload an attachment

        Args:
            filepath (str): Local path to file to upload.
            filename (str, optional): Optionally, specify a new name for the file.

        Returns:
            The newly uploaded Attachment.
        """
        url = f"{self.base_url}/api/v1/experiments/{experiment_id}/attachments"
        file, headers = self._read_multipart_file(filepath, filename)
        return Attachment(self._post(url, data=file, headers=headers))

    def delete_attachment(
        self, experiment_id: str, _id: Optional[str] = None, name: Optional[str] = None
    ) -> None:
        """Delete an attachment"""
        _id = _id or self._get_id_by_name(name, "attachments", experiment_id)
        self._delete(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/attachments/{_id}"
        )

    # ----------------------------- Compensations ------------------------------

    def get_compensations(
        self, experiment_id: str, as_dict: Optional[bool] = False
    ) -> List[Compensation]:
        # TODO Union[List[Compensation], List[Dict[str, Any]]] or get rid of as_dict
        compensations = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/compensations"
        )
        if as_dict:
            return compensations
        return [Compensation(c) for c in compensations]

    def get_compensation(
        self,
        experiment_id: str,
        _id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Compensation:
        if name is not None:
            res = self._get_by_name(name, "compensations", experiment_id)
        elif _id is not None:
            res = self._get(
                f"{self.base_url}/api/v1/experiments/{experiment_id}/compensations/{_id}"  # noqa: E501
            )
        else:
            raise RuntimeError("Either _id or name must be specified.")
        return Compensation(res)

    def post_compensation(self, experiment_id: str, body: Dict[str, Any]):
        res = self._post(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/compensations",
            json=body,
        )
        return Compensation(res)

    # ------------------------------ Experiments -------------------------------

    def get_experiments(self) -> List[Experiment]:
        res = self._get(f"{self.base_url}/api/v1/experiments")
        return [Experiment(experiment) for experiment in res]

    def get_experiment(self, _id=None, name=None) -> Experiment:
        if name is not None:
            res = self._get_by_name(name, "experiments")
        elif _id is not None:
            res = self._get(f"{self.base_url}/api/v1/experiments/{_id}")
        else:
            raise RuntimeError("Either _id or name must be specified.")
        return Experiment(res)

    def post_experiment(self, experiment: dict) -> Experiment:
        """Create a new experiment on CellEngine."""
        res = self._post(f"{self.base_url}/api/v1/experiments", json=experiment)
        return Experiment(res)

    def clone_experiment(self, _id, props: Dict[str, Any] = {}) -> Experiment:
        res = self._post(f"{self.base_url}/api/v1/experiments/{_id}/clone", json=props)
        return Experiment(res)

    def update_experiment(self, _id, body) -> Dict:
        return self._patch(f"{self.base_url}/api/v1/experiments/{_id}", json=body)

    def delete_experiment(self, _id):
        """Marks the experiment as deleted.

        Deleted experiments are permanently deleted after approximately
        7 days. Until then, deleted experiments can be recovered.
        """
        self._delete(f"{self.base_url}/api/v1/experiments/{_id}")

    def save_experiment_revision(self, _id, description: str) -> Dict:
        return self._post(
            f"{self.base_url}/api/v1/experiments/{_id}/revision",
            json={"description": description},
        )

    def import_experiment_resources(
        self,
        experiment_id: str,
        src_experiment_id: str,
        what: ImportOpts,
        channel_map: Optional[Dict[str, str]],
        dst_population_id: Optional[str],
    ) -> None:
        self._post(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/importResources",
            json={
                "srcExperiment": src_experiment_id,
                "channelMap": channel_map,
                "dstPopulationId": dst_population_id,
                "import": what,
            },
        )

    # ------------------------------- FCS Files --------------------------------

    def get_fcs_files(self, experiment_id, as_dict=False) -> List[FcsFile]:
        fcs_files = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/fcsfiles"
        )
        if as_dict:
            return fcs_files
        return [FcsFile(fcs_file) for fcs_file in fcs_files]

    def get_fcs_file(
        self,
        experiment_id: str,
        _id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> FcsFile:
        # TODO this only needs to make one request to do a name lookup
        _id = _id or self._get_id_by_name(name, "fcsfiles", experiment_id)
        fcs_file = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/fcsfiles/{_id}"
        )
        return FcsFile(fcs_file)

    def upload_fcs_file(
        self,
        experiment_id: str,
        filepath_or_data: Union[str, BytesIO],
        filename: Optional[str] = None,
    ) -> FcsFile:
        """Upload an FCS file to CellEngine

        Args:
            filepath_or_data: Local path to FCS file.
            filename: Optionally, specify a new name for the file.

        Returns:
            The newly-uploaded FcsFile
        """
        url = f"{self.base_url}/api/v1/experiments/{experiment_id}/fcsfiles"
        file, headers = self._read_multipart_file(filepath_or_data, filename)
        return FcsFile(self._post(url, data=file, headers=headers))

    def _read_multipart_file(
        self, file: Union[str, BytesIO], filename: Optional[str] = None
    ):
        """Posts a MultipartEncoder of the file and its content-type"""
        if filename is None:
            if isinstance(file, str):
                filename = os.path.basename(file)
            else:
                raise ValueError("filename is required")
        reader = open(file, "rb") if isinstance(file, str) else file
        mpe = MultipartEncoder(
            fields={"data": (filename, reader, "application/octet-stream")}
        )
        return mpe, {"Content-Type": mpe.content_type}

    def create_fcs_file(self, experiment_id, body) -> FcsFile:
        """Creates an FCS file by copying, concatenating and/or
        subsampling existing file(s) from this or other experiments. Can be
        used to import files from other experiments.
        """
        url = f"{self.base_url}/api/v1/experiments/{experiment_id}/fcsfiles"
        return FcsFile(self._post(url, json=body))

    def download_fcs_file(
        self, experiment_id: str, fcs_file_id: str, **kwargs: Any
    ) -> bytes:
        """Download events for a specific FcsFile

        Parameters:
            experiment_id (str): ID of the experiment
            fcs_file_id (str): ID of the FcsFile
            **kwargs:
                - compensatedQ (bool): If true, applies the compensation
                  specified in compensationId to the exported events. For
                  TSV format, the numerical values will be the compensated
                  values. For FCS format, the numerical values will be
                  unchanged, but the file header will contain the
                  compensation as the spill string (file-internal
                  compensation).
                - compensationId (str, optional): Required if populationId is
                    specified. Compensation to use for gating.
                - headers (bool): For TSV format only. If true, a header row
                  containing the channel names will be included.
                - original (bool): If true, the returned file will be
                    byte-for-byte identical to the originally uploaded
                    file. If false or unspecified (and compensatedQ is
                    false, populationId is unspecified and all subsampling
                    parameters are unspecified), the returned file will
                    contain essentially the same data as the originally
                    uploaded file, but may not be byte-for-byte identical.
                    For example, the byte ordering of the DATA segment will
                    always be little-endian and any extraneous information
                    appended to the end of the original file will be
                    stripped. This parameter takes precedence over
                    compensatedQ, populationId and the subsampling
                    parameters.
                - populationId (str): If provided, only events from this
                    population will be included in the output file.
                - postSubsampleN (int): Randomly subsample the file to
                    contain this many events after gating.
                - postSubsampleP (float): Randomly subsample the file to
                    contain this percent of events (0 to 1) after gating.
                - preSubsampleN (int): Randomly subsample the file to contain
                    this many events before gating.
                - preSubsampleP (float): Randomly subsample the file to
                    contain this percent of events (0 to 1) before gating.
                - seed: (int): Seed for random number generator used for
                    subsampling. Use for deterministic (reproducible)
                    subsampling. If omitted, a pseudo-random value is
                    used.
                - addEventNumber (bool): Add an event number column to the
                    exported file. When a populationId is specified
                    (when gating), this number corresponds to the index of
                    the event in the original file.
        """
        params = {}
        if kwargs:
            params = dict(kwargs)

        return self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/fcsfiles/{fcs_file_id}.fcs",  # noqa: E501
            params=params,
            raw=True,
        )

    # ------------------------------ Folders -------------------------------

    def get_folders(self) -> List[Folder]:
        res = self._get(f"{self.base_url}/api/v1/folders")
        return [Folder(folder) for folder in res]

    def get_folder(self, _id=None, name=None) -> Folder:
        if name is not None:
            res = self._get_by_name(name, "folders")
        elif _id is not None:
            res = self._get(f"{self.base_url}/api/v1/folders/{_id}")
        else:
            raise RuntimeError("Either _id or name must be specified.")
        return Folder(res)

    def post_folder(self, folder: dict) -> Folder:
        """Create a new folder on CellEngine."""
        res = self._post(f"{self.base_url}/api/v1/folders", json=folder)
        return Folder(res)

    def update_folder(self, _id, body) -> Dict:
        return self._patch(f"{self.base_url}/api/v1/folders/{_id}", json=body)

    def delete_folder(self, _id):
        """Marks the folder as deleted.

        Deleted folders are permanently deleted after approximately
        7 days. Until then, deleted folders can be recovered.
        """
        self._delete(f"{self.base_url}/api/v1/folders/{_id}")

    # -------------------------------- Gates -----------------------------------

    def get_gates(self, experiment_id, as_dict=False) -> List[Gate]:
        gates = self._get(f"{self.base_url}/api/v1/experiments/{experiment_id}/gates")
        if as_dict:
            return gates
        structured_gates = []
        for gate in gates:
            structured_gates.append(
                self._parse_gate_population(gate)[0]
            )  # return only Gate
        return structured_gates

    def get_gate(self, experiment_id: str, _id: str, as_dict: bool = False) -> Gate:
        """Gates cannot be retrieved by name because all gates in a group of
        tailored gates have the same name, and because compound gates have a
        `names` property instead of a `name` property."""
        gate = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/gates/{_id}"
        )
        if as_dict:
            return gate
        return self._parse_gate_population(gate)[0]  # return only Gate

    def post_gates(
        self,
        experiment_id: str,
        body: List[Dict[str, Any]],
        params: Dict = {},
    ) -> List[Gate]:
        r = self._post(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/gates",
            json=body,
            params=params,
        )
        return [self._parse_gate_population(g)[0] for g in r]

    def post_gate(
        self,
        experiment_id: str,
        body: Dict[str, Any],
        params: Dict = {},
    ) -> Union[Gate, Tuple[Gate, Union[Population, List[Population], None]]]:
        r = self._post(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/gates",
            json=body,
            params=params,
        )
        p = self._parse_gate_population(r)
        if params.get("createPopulation"):
            return p
        else:
            return p[0]

    def delete_gate(
        self,
        experiment_id: str,
        _id: Optional[str] = None,
        gid: Optional[str] = None,
        exclude: Optional[str] = None,
    ) -> None:
        """Deletes a gate or a tailored gate family.

        Specify the top-level gid when working with compound gates (specifying
        the gid of a sector (i.e. one listed in ``model.gids``) will result in no
        gates being deleted). If ``_id`` is specified, only that gate will be
        deleted, regardless of the other parameters specified. May be called as
        a static method from cellengine.Gate or from an Experiment instance.

        Args:
            experiment_id: ID of experiment.
            _id: ID of the gate to delete.
            gid: ID of gate family to delete.
            exclude: Gate ID to exclude from deletion. **Deprecated**. Use the
                    untailoring API instead.

        Example:
            ```python
            cellengine.Gate.delete_gate(experiment_id, gid = [gate family ID])
            # or
            experiment.delete_gate(_id = [gate ID])
            ```

        Returns:
            None
        """
        if exclude:
            warn(
                "'exclude' is deprecated and will be removed in a future release."
                " To untailor gates, use the untailoring API."
            )
        if _id:
            url = f"{self.base_url}/api/v1/experiments/{experiment_id}/gates/{_id}"
        elif gid:
            url = f"{self.base_url}/api/v1/experiments/{experiment_id}/gates?gid={gid}"
            if exclude:
                url = "{0}%exclude={1}".format(url, exclude)
        else:
            raise ValueError("Either _id or gid must be specified.")
        self._delete(url)

    def delete_gates(self, experiment_id: str, ids: List[str]):
        url = f"{self.base_url}/api/v1/experiments/{experiment_id}/gates/"
        [self._delete(url + _id) for _id in ids]

    def _parse_gate_population(
        self, res: Any
    ) -> Tuple[Gate, Union[Population, List[Population], None]]:
        keys = res.keys()
        if "population" in keys:
            gate = res["gate"]
            pop = Population(res["population"])
        elif "populations" in keys:
            gate = res["gate"]
            pop = [Population(p) for p in res["populations"]]
        else:
            gate = res
            pop = None
        module = importlib.import_module("cellengine")
        gate_subclass = getattr(module, gate["type"])
        return (
            gate_subclass(gate),
            pop,
        )

    def update_gate_family(self, experiment_id, gid, body: dict = {}) -> dict:
        return self._patch(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/gates?gid={gid}",
            json=body,
        )

    def apply_tailoring(
        self, experiment_id: str, gate: Gate, fcs_file_ids: List[str]
    ) -> ApplyTailoringRes:
        """Tailor a gate to a file or files."""
        return self._post(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/gates/applyTailored",
            params={"gid": gate.gid},
            json={"gate": gate._properties, "fcsFileIds": fcs_file_ids},
        )

    # -------------------------------- Plots -----------------------------------

    def get_plot(
        self,
        experiment_id: str,
        fcs_file_id: str,
        plot_type: str,
        x_channel: str,
        y_channel: str,
        z_channel: Optional[str] = None,
        population_id: Optional[str] = None,
        compensation: Union[str, Literal[-1], Literal[0]] = 0,
        properties: Optional[Dict] = None,
        raw=False,
    ) -> Plot:

        req_params = {
            "fcsFileId": fcs_file_id,
            "xChannel": x_channel,
            "yChannel": y_channel,
            "zChannel": y_channel,
            "plotType": plot_type,
            "populationId": population_id,
            "compensation": compensation,
        }

        if properties:
            req_params.update(properties)

        data = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/plot",
            params=req_params,
            raw=True,
        )
        if raw:
            return data
        return Plot(
            experiment_id=experiment_id,
            fcs_file_id=fcs_file_id,
            plot_type=plot_type,
            x_channel=x_channel,
            y_channel=y_channel,
            z_channel=z_channel,
            population_id=population_id,
            compensation=compensation,
            data=data,
        )

    # ----------------------------- Populations --------------------------------

    def get_populations(self, experiment_id) -> List[Population]:
        populations: List[Dict[str, Any]] = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/populations"
        )
        return [Population(pop) for pop in populations]

    def get_population(self, experiment_id, _id=None, name=None) -> Population:
        _id = _id or self._get_id_by_name(name, "populations", experiment_id)
        population = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/populations/{_id}"
        )
        return Population(population)

    def post_population(self, experiment_id, population: Dict[str, Any]) -> Population:
        res = self._post(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/populations",
            json=population,
        )
        return Population(res)

    # ------------------------------ ScaleSets ---------------------------------

    def get_scaleset(self, experiment_id: str) -> ScaleSet:
        """Get the scaleset for an experiment."""
        scaleset = self._get(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/scalesets"
        )[0]
        return ScaleSet(scaleset)

    # ------------------------------ Statistics --------------------------------

    def get_statistics(
        self,
        experiment_id: str,
        statistics: List[str],
        channels: List[str],
        q: Optional[float] = None,
        annotations: bool = False,
        compensation_id: Union[Compensations, str] = UNCOMPENSATED,
        fcs_file_ids: Optional[List[str]] = None,
        format: str = "json",
        layout: Optional[str] = None,
        percent_of: Optional[Union[str, List[str]]] = "PARENT",
        population_ids: Optional[List[str]] = None,
    ) -> Union[Dict, str, DataFrame]:
        """
        Request Statistics from CellEngine.

        Args:
            experiment_id: ID of the experiment.
            statistics: Statistics to calculate. Any of "mean", "median",
                "quantile", "mad" (median absolute deviation), "geometricmean",
                "eventcount", "cv", "stddev" or "percent" (case-insensitive).
            q (int): quantile (required for "quantile" statistic)
            channels (List[str]): for "mean", "median", "geometricMean",
                "cv", "stddev", "mad" or "quantile" statistics. Names of channels
                to calculate statistics for.
            annotations: Include file annotations in output
                (defaults to False).
            compensation_id: Compensation to use for gating and statistics
                calculation. Defaults to uncompensated. In addition to a
                compensation ID, three special constants may be used:
                    [`UNCOMPENSATED`][cellengine.UNCOMPENSATED],
                    [`FILE_INTERNAL`][cellengine.FILE_INTERNAL] or
                    [`PER_FILE`][cellengine.PER_FILE].
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

        if "quantile" == statistics and not isinstance(q, float):
            raise ValueError("'q' must be a number for 'quantile' statistic.")

        params = {
            "statistics": statistics,
            "q": q,
            "channels": channels,
            "annotations": annotations,
            "compensationId": compensation_id,
            "fcsFileIds": fcs_file_ids,
            "format": "json" if format == "pandas" else format,
            "layout": layout,
            "percentOf": percent_of,
            "populationIds": population_ids,
        }
        req_params = {key: val for key, val in params.items() if val is not None}

        raw_stats = self._post(
            f"{self.base_url}/api/v1/experiments/{experiment_id}/bulkstatistics",
            json=req_params,
            raw=True,
        )

        format = format.lower()
        if format == "json":
            return json.loads(raw_stats)
        elif "sv" in format:
            try:
                return raw_stats.decode()
            except Exception as e:
                raise ValueError("Invalid output format {}".format(format), e)
        elif format == "pandas":
            try:
                return pandas.DataFrame.from_dict(json.loads(raw_stats))
            except Exception as e:
                raise ValueError("Invalid data format {} for pandas".format(format), e)
        else:
            raise ValueError("Invalid data format selected.")
