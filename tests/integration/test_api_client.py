from cellengine.utils.api_client.APIClient import APIClient
from cellengine.resources.experiment import Experiment


def test_client_get_experiments(client: APIClient):
    experiments = client.get_experiments()
    assert all([type(exp) is Experiment for exp in experiments])
