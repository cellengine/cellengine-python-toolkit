import os
import pytest
import responses
from cellengine.utils.api_client.APIClient import APIClient


"""
Run tests with ``pytest``.

Fixtures are defined in cellengine-python-toolkit/tests/tests/fixtures.
You can write new fixtures in new files here, or in existing .py files.
Fixtures in the ..tests/fixtures folder can use other fixtures in that folder.

Fixtures must be imported below using the `pytest_plugins` list.
When writing new fixtures, the ``pytest-vcr`` plugin is not called, as
it is with other tests. Use the "fixture_vcr" instance of VCR to write fixtures.

When writing new tests, ``pytest-vcr`` hooks tests to VCR. Use the
@pytest.mark.vcr decorator to make a .yaml with the same name as the test.

For unknown reasons, ``pytest-vcr`` fails to filter the headers for a
DELETE requests. Thus, "test_base_delete" is an unsafe test, as it saves a
login token. I have opened an issue on ``pytest-vcr``, but for now, if you
remake "test_base_delete.yaml", delete the two lines with the login token.
"""

collect_ignore_glob = ["*integration.py"]

pytest_plugins = [
    "fixtures.api-experiments",
    "fixtures.api-fcsfiles",
    "fixtures.api-compensations",
    "fixtures.api-gates",
    "fixtures.api-scalesets",
    "fixtures.api-populations",
    "fixtures.api-attachments",
    "fixtures.api-statistics",
    "fixtures.api-events",
]


@pytest.fixture(scope="session")
def ENDPOINT_BASE():
    return os.environ.get("CELLENGINE_BASE_URL", "https://cellengine.com/api/v1")


@pytest.fixture(scope="session")
def client(ENDPOINT_BASE):
    with responses.RequestsMock() as resps:
        resps.add(
            responses.POST,
            ENDPOINT_BASE + "/signin",
            json={
                "token": "some token",
                "userId": 123456789,
                "admin": True,
                "flags": {},
            },
            status=200,
        )
        return APIClient(user_name="gegnew", password="testpass1")


@pytest.fixture(scope="session")
def experiment(ENDPOINT_BASE, client, experiments):
    with responses.RequestsMock() as resps:
        resps.add(
            responses.GET,
            ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b",
            json=experiments[0],
            status=200,
        )
        return client.get_experiment(_id="5d38a6f79fae87499999a74b")


@pytest.fixture(scope="module")
def vcr_config():
    """Pytest hook for vcr config"""
    return {
        "filter_headers": ["Cookie"],
        "before_record_response": scrub_header("set-cookie", repl="safetoken"),
        "cassette_library_dir": "tests/cassettes",
        "record_mode": "overwrite",
    }


def scrub_header(string, repl=""):
    """Remove secrets from stored vcr cassettes"""

    def before_record_response(response):
        response["headers"][string] = repl
        return response

    return before_record_response


def scrub_client_request():
    def before_record_response(response):
        response["headers"]["set-cookie"] = "safetoken"
        response["body"]["string"] = None
        return response

    return before_record_response
