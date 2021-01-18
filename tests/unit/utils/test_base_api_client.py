import pytest
import requests
import responses

from cellengine.utils.api_client.APIError import APIError


MOCK_DATA = {"data": "some fake data"}
BASE_URL = "http://fake/"
SESSION = requests.Session()


def test_api_client(client):
    assert client._API_NAME == "CellEngine Python Toolkit"


@responses.activate
def test_should_get_raw(client):
    responses.add(responses.GET, BASE_URL + "test", json=MOCK_DATA)
    res = client._get("http://fake/test")
    assert res == MOCK_DATA


@responses.activate
def test_should_raise_on_empty_response(client):
    responses.add(responses.GET, BASE_URL + "test")
    with pytest.raises(APIError, match=r"200.*JSONDecodeError"):
        assert "" == client._get("http://fake/test")


@responses.activate
def test_should_raise_custom_message(client):
    mock_data = {"error": {"message": "some error"}}
    responses.add(responses.GET, BASE_URL + "test", status=500, json=mock_data)
    with pytest.raises(APIError, match=r"500.*some error"):
        assert client._get("http://fake/test") == ""


@responses.activate
def test_should_get(client):
    responses.add(responses.GET, BASE_URL + "test", json=MOCK_DATA)
    assert client._get("http://fake/test") == {"data": "some fake data"}


@responses.activate
def test_should_post(client):
    body = {"some": "body"}
    responses.add(responses.POST, BASE_URL + "test", json=body)
    assert client._post("http://fake/test", body) == {"some": "body"}


@responses.activate
def test_should_patch(client):
    body = {"some": "body"}
    responses.add(responses.PATCH, BASE_URL + "test", json=body)
    assert client._patch("http://fake/test", body) == {"some": "body"}


@responses.activate
def test_should_delete(client):
    responses.add(responses.DELETE, BASE_URL + "test", json="deleted")
    assert client._delete("http://fake/test") == b'"deleted"'
