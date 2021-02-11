from abc import abstractmethod
from typing import Union, List, Dict

import requests
from cellengine.utils.singleton import AbstractSingleton
from cellengine.utils.api_client.APIError import APIError
from cellengine import __version__ as CEV


class BaseAPIClient(metaclass=AbstractSingleton):
    @property
    @abstractmethod
    def _API_NAME(self):
        """Define this property in subclasses"""
        assert self._API_NAME

    def __init__(self):
        self.requests_session = requests.Session()
        self.requests_session.headers.update(
            {
                "Content-Type": "application/json",
                # fmt: off
                "User-Agent":
                f"CellEngine Python API Toolkit/{CEV} requests/{requests.__version__}",
                # fmt: on
            }
        )

    def close(self):
        self.requests_session.close()

    @staticmethod
    def _make_headers(headers):
        request_headers = {}
        if headers is not None:
            request_headers.update(headers)
        return request_headers

    def _parse_response(self, response, raw=False):
        success = 200 <= response.status_code < 300

        if success and raw:
            return response.content

        try:
            response_json = response.json()

            if success:
                return response_json
            else:
                raise APIError(
                    response.url, response.status_code, response_json["error"]
                )
        except APIError:
            raise
        except Exception as error:
            raise APIError(response.url, response.status_code, repr(error))

    def _get(
        self, url, params: Dict = None, headers: Dict = None, raw=False
    ) -> Union[Dict, List[Dict], bytes]:
        try:
            response = self.requests_session.get(
                url,
                headers=self._make_headers(headers),
                params=params if params else {},
            )
        except Exception as error:
            raise error
        return self._parse_response(response, raw=raw)

    def _post(
        self,
        url,
        json: Union[Dict, List[Dict]] = None,
        params: Dict = None,
        headers: Dict = None,
        files: Dict = None,
        data=None,
        raw=False,
    ) -> Dict:
        response = self.requests_session.post(
            url,
            json=json,
            headers=self._make_headers(headers),
            params=params if params else {},
            files=files,
            data=data,
        )
        return self._parse_response(response, raw=raw)

    def _patch(
        self,
        url,
        json: Union[Dict, List[Dict]] = None,
        params: Dict = None,
        headers: Dict = None,
        files: Dict = None,
        raw=False,
    ) -> Dict:
        response = self.requests_session.patch(
            url,
            json=json,
            headers=self._make_headers(headers),
            params=params if params else {},
            files=files,
        )
        return self._parse_response(response, raw=raw)

    def _delete(
        self, url, params: dict = None, headers: dict = None, raw=False
    ) -> dict:
        response = self.requests_session.delete(
            url, headers=self._make_headers(headers), params=params if params else {},
        )
        try:
            if response.ok:
                return response.content
            else:
                raise APIError(
                    response.url, response.status_code, response["error"]["message"]
                )
        except APIError:
            raise
        except Exception as error:
            raise APIError(response.url, response.status_code, repr(error))

    # This shouldn't necessarily be here, but it allows doc_inherit to get the
    # docstring for this method
    @abstractmethod
    def get_statistics():
        """
        Request Statistics from CellEngine.

        Args:
            experiment_id: ID of experiment to request statistics for.
            statistics: Statistical method to request. Any of "mean", "median",
                "quantile", "mad" (median absolute deviation), "geometricmean",
                "eventcount", "cv", "stddev" or "percent" (case-insensitive).
            q: int: quantile (required for "quantile" statistic)
            channels: str or List[str]: for "mean", "median", "geometricMean", "cv",
                "stddev", "mad" or "quantile" statistics. Names of
                channels to calculate statistics for.
            annotations (optional): bool: Include file annotations in output
                (defaults to False).
            compensation_id (optional): str: Compensation to use for gating and
                statistic calculation.
                Defaults to uncompensated. Three special constants may be used:
                    0: Uncompensated
                    -1: File-Internal Compensation Uses the file's internal
                        compensation matrix, if available. If not, an error
                        will be returned.
                    -2: Per-File Compensation Use the compensation assigned to
                        each individual FCS file.
            fcs_file_ids (optional): List[str]: FCS files to get statistics for. If
                omitted, statistics for all non-control FCS files will be returned.
            format (optional): str: One of "TSV (with[out] header)",
                "CSV (with[out] header)" or "json" (default), "pandas",
                case-insensitive.
            layout (optional): str: The file (TSV/CSV) or object (JSON) layout.
                One of "tall-skinny", "medium", or "short-wide".
            percent_of (optional): str or List[str]: Population ID or array of
                population IDs.  If omitted or the string "PARENT", will calculate
                percent of parent for each population. If a single ID, will calculate
                percent of that population for all populations specified by
                population_ids. If a list, will calculate percent of each of
                those populations.
            population_ids (optional): List[str]: List of population IDs.
                Defaults to ungated.
        Returns:
            statistics: Dict, String, or pandas.Dataframe
        """
        pass
