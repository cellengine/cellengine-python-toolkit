from cellengine.resources.experiment import Experiment
import os
import socket
import pytest
import responses
from cellengine.utils.api_client.APIClient import APIClient


"""
Run tests with ``pytest``.

Fixtures are defined in cellengine-python-toolkit/tests/tests/fixtures.
You can write new fixtures in new files here, or in existing .py files.
Fixtures in the ..tests/fixtures folder can use other fixtures in that folder.

When writing new tests, ``pytest-recording`` hooks tests to VCR. Use the
@pytest.mark.vcr decorator to automatically make a .yaml with the same name
as the test. When writing VCR tests, you need to have an authorized APIClient
instance the first time you run tests (to record actual API interactions).
Do this by replacing the return value of the ``client`` fixture below
to an APIClient() with valid credentials.

To be completely sure that real HTTP requests are not made, you can use the
``block_request`` fixture, which monkey-patches the ``socket`` object. It is
best used with the ``@pytest.mark.usefixtures("block_request")`` decorator.
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
    "fixtures.spillstring",
    "fixtures.compensated_events",
    "fixtures.novocyte",
]


@pytest.fixture(scope="session")
def block_request():
    def guard(*args, **kwargs):
        raise Exception("I told you not to use the Internet!")

    socket.socket = guard


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
        return APIClient(username="gegnew", password="testpass1")


@pytest.fixture(scope="session")
def experiment(experiments):
    return Experiment.from_dict(experiments[0])


@pytest.fixture(scope="module")
def vcr_config():
    """Pytest hook for vcr config"""
    return {
        "filter_headers": ["Cookie", "authorization"],
        "ignore_localhost": True,
        "record_mode": "once",
        "before_record_response": scrub_header("set-cookie", repl="safetoken"),
        "cassette_library_dir": "tests/cassettes",
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
