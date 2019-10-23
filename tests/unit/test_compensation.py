import os
import pytest
import responses
import pandas
import cellengine


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@pytest.fixture(scope="module")
def compensation(experiment, compensations):
    with responses.RequestsMock() as resps:
        resps.add(
            responses.GET,
            base_url + "experiments/5d38a6f79fae87499999a74b/compensations",
            json=compensations,
        )
        return experiment.compensations[0]


@responses.activate
def test_all_experiment_properties(compensation):
    assert type(compensation._properties) is dict
    assert type(compensation) is cellengine.Compensation
    assert hasattr(compensation, "_id")
    assert hasattr(compensation, "name")
    assert hasattr(compensation, "experiment_id")
    assert hasattr(compensation, "channels")
    assert hasattr(compensation, "N")
    assert compensation.N == len(compensation.dataframe)
    assert hasattr(compensation, "dataframe")
    assert type(compensation.dataframe) is pandas.core.frame.DataFrame
    assert all(compensation.dataframe.index == compensation.channels)
    assert hasattr(compensation, "apply")
    assert hasattr(compensation, "dataframe_as_html")
