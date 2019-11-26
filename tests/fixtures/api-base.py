import os
import pytest
import responses
import cellengine

base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@pytest.fixture(scope="session")
def client():
    with responses.RequestsMock() as resps:
        resps.add(
            responses.POST,
            base_url + "signin",
            json={
                "token": "s:qbpXFuiS4zBujLjLUx4K8pldGl4hdqrW",
                "userId": "5d366077a1789f7d6653075c",
                "admin": True,
                "flags": {},
            },
            status=200,
        )
        client = cellengine.Client(username="gegnew", password="testpass1")
        return client


@pytest.fixture(scope="session")
def experiment(client, experiments):
    with responses.RequestsMock() as resps:
        resps.add(
            responses.GET,
            base_url + "experiments/5d38a6f79fae87499999a74b",
            json=experiments[0],
        )
        experiment = client.get_experiment(_id="5d38a6f79fae87499999a74b")
        return experiment
