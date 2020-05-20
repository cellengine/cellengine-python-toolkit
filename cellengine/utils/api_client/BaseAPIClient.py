from abc import abstractmethod, ABCMeta
from typing import Union, List, Dict

import requests
from cellengine.utils.singleton import Singleton
from cellengine.utils.api_client.APIError import APIError


class AbstractSingleton(Singleton, ABCMeta):
    pass


class BaseAPIClient(metaclass=AbstractSingleton):
    @property
    @abstractmethod
    def API_NAME(self):
        """Define this property in subclasses"""

        assert self.API_NAME

    def __init__(self):
        self.requests_session = requests.Session()
        self.requests_session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "CellEngine Python API Toolkit/0.1.1 requests/{0}".format(
                    requests.__version__
                ),
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
            json = response.json()

            if success:
                return json
            else:
                raise APIError(
                    response.url, response.status_code, json["error"]["message"]
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
        raw=False,
    ) -> Dict:
        response = self.requests_session.post(
            url,
            json=json,
            headers=self._make_headers(headers),
            params=params if params else {},
            files=files,
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
