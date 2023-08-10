from cellengine.resources.experiment import Experiment
import pytest
import uuid
from cellengine.utils.api_client.APIClient import APIClient
from typing import Iterator, Tuple


"""
Run tests with ``pytest``.

Unit tests are in the process of being removed in favor of integration tests
because it's a pain to keep the unit test recordings up to date with the API.

Fixtures are defined in cellengine-python-toolkit/tests/tests/fixtures.
You can write new fixtures in new files here, or in existing .py files.
Fixtures in the ..tests/fixtures folder can use other fixtures in that folder.
Avoid using fixtures for anything returned by the API.
"""

collect_ignore_glob = ["unit/*"]

pytest_plugins = []


@pytest.fixture(scope="session")
def client() -> APIClient:
    return APIClient()


@pytest.fixture(scope="session")
def run_id() -> str:
    return uuid.uuid4().hex[:5]


@pytest.fixture()
def test_id() -> str:
    return uuid.uuid4().hex[:5]


@pytest.fixture()
def blank_experiment(test_id: str, client: APIClient) -> Iterator[Experiment]:
    exp_name = f"Ligands {test_id}"
    print(f"Setting up CellEngine experiment {exp_name}")
    exp = Experiment.create(exp_name)

    yield exp

    print(f"Starting teardown of {exp_name}")
    client.delete_experiment(exp._id)
