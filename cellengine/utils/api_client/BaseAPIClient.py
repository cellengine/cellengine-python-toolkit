from __future__ import annotations
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Union

import requests
from requests import Response
from requests.sessions import HTTPAdapter

from cellengine import __version__ as CEV
from cellengine.utils.api_client.APIError import APIError
from cellengine.utils.singleton import AbstractSingleton


def prepare_params(params: Dict) -> Dict:
    """Converts Boolean values to lower-case strings (whereas `requests` yields
    upper-case)."""
    return {k: str(v).lower() if type(v) == bool else v for k, v in params.items()}


class BaseAPIClient(metaclass=AbstractSingleton):
    @property
    @abstractmethod
    def _API_NAME(self):
        """Define this property in subclasses"""
        assert self._API_NAME

    def __init__(self):
        self.requests_session = requests.Session()
        self.requests_session.mount("http://", HTTPAdapter(max_retries=3))
        self.requests_session.mount("https://", HTTPAdapter(max_retries=3))
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

    def _parse_response(self, response: Response, raw: bool = False) -> Any:
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
        self,
        url,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        raw=False,
    ) -> Any:
        try:
            response = self.requests_session.get(
                url,
                headers=self._make_headers(headers),
                params=prepare_params(params or {}),
            )
        except Exception as error:
            raise error
        return self._parse_response(response, raw=raw)

    def _post(
        self,
        url,
        json: Optional[Union[Dict, List[Dict]]] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        files: Optional[Dict] = None,
        data=None,
        raw=False,
    ) -> Any:
        response = self.requests_session.post(
            url,
            json=json,
            headers=self._make_headers(headers),
            params=prepare_params(params or {}),
            files=files,
            data=data,
        )
        return self._parse_response(response, raw=raw)

    def _patch(
        self,
        url,
        json: Union[Dict, List[Dict]],
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        files: Optional[Dict] = None,
        raw=False,
    ):
        response = self.requests_session.patch(
            url,
            json=json,
            headers=self._make_headers(headers),
            params=prepare_params(params or {}),
            files=files,
        )
        return self._parse_response(response, raw=raw)

    def _delete(
        self, url, params: Optional[dict] = None, headers: Optional[dict] = None
    ):
        response = self.requests_session.delete(
            url,
            headers=self._make_headers(headers),
            params=prepare_params(params or {}),
        )
        try:
            if response.ok:
                return response.content
            else:
                raise APIError(response.url, response.status_code, response.json())
        except APIError:
            raise
        except Exception as error:
            raise APIError(response.url, response.status_code, repr(error))
