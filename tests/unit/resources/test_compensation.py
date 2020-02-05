import os
import json
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


def properties_tester(comp):
    assert type(comp._properties) is dict
    assert type(comp) is cellengine.Compensation
    assert hasattr(comp, "_id")
    assert hasattr(comp, "name")
    assert hasattr(comp, "experiment_id")
    assert hasattr(comp, "channels")
    assert hasattr(comp, "N")
    assert comp.N == len(comp.dataframe)
    assert hasattr(comp, "dataframe")
    assert type(comp.dataframe) is pandas.core.frame.DataFrame
    assert all(comp.dataframe.index == comp.channels)
    assert hasattr(comp, "apply")
    assert hasattr(comp, "dataframe_as_html")

def test_compensation_properties(compensation):
    properties_tester(compensation)

@responses.activate
def test_update_compensation(experiment, compensation):
    """Test that the .update() method makes the correct call. Does not test
    that the correct response is made; this should be done with an integration
    test.
    """
    # patch the mocked response with the correct values
    response = compensation._properties.copy()
    response.update({"name": "newname"})
    responses.add(
        responses.PATCH,
        base_url
        + "experiments/5d64abe2ca9df61349ed8e78/compensations/{0}".format(
            compensation._id
        ),
        json=response,
    )
    compensation.name = "newname"
    compensation.update()
    properties_tester(compensation)
    assert json.loads(responses.calls[0].request.body) == compensation._properties
