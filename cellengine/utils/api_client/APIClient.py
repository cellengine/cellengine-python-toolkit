import os
import json
import pandas
from getpass import getpass
from typing import List, Dict, Union
from functools import lru_cache

from cellengine.utils.api_client.BaseAPIClient import BaseAPIClient
from cellengine.utils.api_client.APIError import APIError
from cellengine.utils.singleton import Singleton
from cellengine.resources.attachment import Attachment
from cellengine.resources.compensation import Compensation
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcsfile import FcsFile
from cellengine.resources.gate import Gate
from cellengine.resources.plot import Plot
from cellengine.resources.population import Population


class APIClient(BaseAPIClient, metaclass=Singleton):
    API_NAME = "Cellengine Python Toolkit"

    def __init__(self, user_name=None, password=None, token=None):
        super(APIClient, self).__init__()
        self.endpoint_base = os.environ.get(
            "BASE_URL", "https://cellengine.com/api/v1"
        )
        self.user_name = user_name
        self.password = password
        self.token = token
        self.user_id = None
        self.admin = None
        self.flags = None
        self.authenticated = self._authenticate(user_name, password, token)

        self.cache_info = self._get_id_by_name.cache_info
        self.cache_clear = self._get_id_by_name.cache_clear

    def __repr__(self):
        if self.user_name:
            return f"Client(user={self.user_name})"
        else:
            return f"Client(TOKEN)"

    def _authenticate(self, user_name, password, token):
        """Authenticate with the CellEngine API.

        There are three ways of authenticating:
            1. Username and password. Use this to authenticate a user.
            2. API token. Use this to authenticate an application that is
                not associated with a user, such as a LIMS integration.
            3. Auto-authorization. If you are running a Jupyter CellEngine
                session, you will be automatically authorized as your
                user account.

        Args:
            username: Login credential set during CellEngine registration
            password: Password for login
            token: Authentication token; may be passed instead of username and password

        Attributes:
            experiments: List all experiments on the client

        Returns:
            client: Authenticated client object
        """
        if user_name:
            self.user_name = user_name
            self.password = password or getpass()

            res = self._post(
                f"{self.endpoint_base}/signin",
                {"username": self.user_name, "password": self.password},
            )

            self.token = res["token"]
            self.user_id = res["userId"]
            self.admin = res["admin"]
            self.flags = res["flags"]

        elif token:
            self.requests_session.cookies.update({"token": "{0}".format(token)})

        else:
            raise APIError("Authentication failed: Username or token must be provided.")
        return True

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
            raise e

    def _lookup_by_name(self, path, query, name):
        params = f'query=eq({query},"{name}")&limit=2'
        return self._get(f"{self.endpoint_base}/{path}", params=params)

    def _handle_response(self, response):
        if type(response) is list:
            self._handle_list(response)
        else:
            response = [response]
        return response[0]

    def _handle_list(self, response: List) -> RuntimeError:
        if len(response) == 0:
            raise RuntimeError("No objects found.")
        elif len(response) > 1:
            raise RuntimeError("Multiple objects found; use _id to query instead.")

    def update_entity(self, experiment_id, _id, entity_type, body) -> dict:
        return self._patch(
            f"{self.endpoint_base}/experiments/{experiment_id}/{entity_type}/{_id}",
            json=body,
        )

    def delete_entity(self, experiment_id, entity_type, _id):
        url = f"{self.endpoint_base}/experiments/{experiment_id}/{entity_type}/{_id}"
        self._delete(url)

    def get_attachments(self, experiment_id, as_dict=False) -> List[Attachment]:
        attachments = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/attachments"
        )
        if as_dict:
            return attachments
        return [Attachment(attachment) for attachment in attachments]

    def get_attachment(
        self, experiment_id, _id=None, name=None, as_dict=False
    ) -> Attachment:
        _id = _id or self._get_id_by_name(name, "attachments", experiment_id)
        attachment = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/attachments/{_id}"
        )
        if as_dict:
            return attachment
        return Attachment(attachment)

    def post_attachment(self, experiment_id, files):
        url = f"{self.endpoint_base}/experiments/{experiment_id}/attachments"
        att = self._post(url, files=files)
        return Attachment(att)

    def get_compensations(self, experiment_id, as_dict=False) -> List[Compensation]:
        compensations = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/compensations"
        )
        if as_dict:
            return compensations
        return [Compensation(comp) for comp in compensations]

    def get_compensation(
        self, experiment_id, _id=None, name=None, as_dict=False
    ) -> Compensation:
        _id = _id or self._get_id_by_name(name, "compensations", experiment_id)
        comp = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/compensations/{_id}"
        )
        if as_dict:
            return comp
        return Compensation(comp)

    def post_compensation(
        self, experiment_id, compensation=None, as_dict=False
    ) -> Compensation:
        res = self._post(
            f"{self.endpoint_base}/experiments/{experiment_id}/compensations",
            json=compensation,
        )
        if as_dict:
            return res
        return Compensation(res)

    def get_experiments(self, as_dict=False) -> List[Experiment]:
        experiments = self._get(f"{self.endpoint_base}/experiments")
        if as_dict:
            return experiments
        return [Experiment(experiment) for experiment in experiments]

    def get_experiment(self, _id=None, name=None, as_dict=False) -> Experiment:
        _id = _id or self._get_id_by_name(name, "experiments", _id)
        experiment = self._get(f"{self.endpoint_base}/experiments/{_id}")
        if as_dict:
            return experiment
        return Experiment(experiment)

    def post_experiment(self, experiment: dict, as_dict=False) -> Experiment:
        experiment = self._post(f"{self.endpoint_base}/experiments", json=experiment)
        if as_dict:
            return experiment
        return Experiment(experiment)

    def update_experiment(self, _id, body) -> Dict:
        return self._patch(f"{self.endpoint_base}/experiments/{_id}", json=body)

    def get_fcsfiles(self, experiment_id, as_dict=False) -> List[FcsFile]:
        fcsfiles = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/fcsfiles"
        )
        if as_dict:
            return fcsfiles
        return [FcsFile(fcsfile) for fcsfile in fcsfiles]

    def get_fcsfile(self, experiment_id, _id=None, name=None, as_dict=False) -> FcsFile:
        _id = _id or self._get_id_by_name(name, "fcsfiles", experiment_id)
        fcsfile = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/fcsfiles/{_id}"
        )
        if as_dict:
            return fcsfile
        return FcsFile(fcsfile)

    def upload_fcsfile(self, experiment_id, file):
        url = f"{self.endpoint_base}/experiments/{experiment_id}/fcsfiles"
        f = self._post(url, files=file)
        return FcsFile(f)

    def create_fcsfile(self, experiment_id, body):
        url = f"{self.endpoint_base}/experiments/{experiment_id}/fcsfiles"
        return self._post(url, json=body)

    def get_gates(self, experiment_id, as_dict=False) -> List[Gate]:
        gates = self._get(f"{self.endpoint_base}/experiments/{experiment_id}/gates")
        if as_dict:
            return gates
        return [Gate.build(gate) for gate in gates]

    def get_gate(self, experiment_id, _id, as_dict=False) -> Gate:
        """Gates cannot be retrieved by name."""
        gate = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/gates/{_id}"
        )
        if as_dict:
            return gate
        return Gate.build(gate)

    def delete_gate(self, experiment_id, _id):
        url = f"{self.endpoint_base}/experiments/{experiment_id}/gates/{_id}"
        self._delete(url)

    def post_gate(
        self, experiment_id, gate: Dict, create_population=True, as_dict=False
    ) -> Gate:
        res = self._post(
            f"{self.endpoint_base}/experiments/{experiment_id}/gates",
            json=gate,
            params={"createPopulation": create_population},
        )
        if as_dict:
            return res
        return Gate.build(res)

    def get_plot(
        self,
        experiment_id,
        fcsfile_id,
        x_channel: str,
        y_channel: str,
        plot_type: str,
        population_id: str = None,
        properties: Dict = None,
        as_dict=False,
    ) -> Plot:

        req_params = {
            "fcsFileId": fcsfile_id,
            "xChannel": x_channel,
            "yChannel": y_channel,
            "plotType": plot_type,
            "populationId": population_id,
        }

        if properties:
            req_params.update(properties)

        data = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/plot",
            params=req_params,
            raw=True,
        )
        if as_dict:
            return data
        return Plot(
            experiment_id,
            fcsfile_id,
            x_channel,
            y_channel,
            plot_type,
            population_id,
            data,
        )

    def get_populations(self, experiment_id, as_dict=False) -> List[Population]:
        populations = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/populations"
        )
        if as_dict:
            return populations
        return [Population(pop) for pop in populations]

    def get_population(
        self, experiment_id, _id=None, name=None, as_dict=False
    ) -> Population:
        _id = _id or self._get_id_by_name(name, "populations", experiment_id)
        population = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/populations/{_id}"
        )
        if as_dict:
            return population
        return Population(population)

    def post_population(self, experiment_id, population: Dict, as_dict=False) -> Gate:
        res = self._post(
            f"{self.endpoint_base}/experiments/{experiment_id}/populations",
            json=population,
        )
        if as_dict:
            return res
        return Population(res)

    def get_statistics(
        self,
        experiment_id: str,
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

        Required Args:
            experiment_id: ID of experiment to request statistics for.
            statistics: Statistical method to request. Any of "mean", "median", "quantile",
                "mad" (median absolute deviation), "geometricmean", "eventcount",
                "cv", "stddev" or "percent" (case-insensitive).
            q: int: quantile (required for "quantile" statistic)
            channels: str or List[str]: for "mean", "median", "geometricMean", "cv",
                "stddev", "mad" or "quantile" statistics. Names of
                channels to calculate statistics for.
        Optional Args:
            annotations: bool: Include file annotations in output (defaults to False).
            compensation_id: str: Compensation to use for gating and statistic calculation.
                Defaults to uncompensated. Three special constants may be used:
                    0: Uncompensated
                    -1: File-Internal Compensation Uses the file's internal compensation
                        matrix, if available. If not available, an error will be returned.
                    -2: Per-File Compensation Use the compensation assigned to each
                        individual FCS file.
            fcs_file_ids: List[str]: FCS files to get statistics for. If omitted,
                statistics for all non-control FCS files will be returned.
            format: str: One of "TSV (with[out] header)", "CSV (with[out] header)" or
                "json" (default), "pandas", case-insensitive.
            layout: str: The file (TSV/CSV) or object (JSON) layout. One of "tall-skinny",
                "medium", or "short-wide".
            percent_of: str or List[str]: Population ID or array of population IDs.
                If omitted or the string "PARENT", will calculate percent of parent for
                each population. If a single ID, will calculate percent of that population
                for all populations specified by populationIds. If a list, will calculate
                percent of each of those populations.
            population_ids: List[str]: List of population IDs. Defaults to ungated.
        Returns:
            statistics: Dict, String, or pandas.Dataframe
        """

        def determine_format(f):
            if f == "pandas":
                return "json"
            else:
                return f

        if "quantile" == statistics:
            try:
                assert q
            except AssertionError:
                raise ValueError(
                    "'q' is a required parameter for 'quantile' statistics."
                )

        params = {
            "statistics": statistics,
            "q": q,
            "channels": channels,
            "annotations": annotations,
            "compensationId": compensation_id,
            "fcsFileIds": fcs_file_ids,
            "format": determine_format(format),
            "layout": layout,
            "percentOf": percent_of,
            "populationIds": population_ids,
        }
        req_params = {key: val for key, val in params.items() if val is not None}

        raw_stats = self._post(
            f"{self.endpoint_base}/experiments/{experiment_id}/bulkstatistics",
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

    def get_scalesets(self, experiment_id, as_dict=True) -> List[Dict]:
        """Get scalesets for an experiment.
        TODO: for now, this always returns the raw data
        """
        scalesets = self._get(
            f"{self.endpoint_base}/experiments/{experiment_id}/scalesets"
        )
        if as_dict:
            return scalesets
        else:
            raise NotImplementedError(
                "There is no SDK representation of Scalesets yet."
            )
