import os
import json
import pytest
import responses
import cellengine


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@pytest.fixture(scope="module")
def population(experiment, populations):
    with responses.RequestsMock() as resps:
        resps.add(
            responses.GET,
            base_url + "experiments/5d38a6f79fae87499999a74b/populations",
            json=populations,
        )
        return experiment.populations[0]


def test_all_population_properties(population):
    assert type(population._properties) is dict
    assert type(population) is cellengine.Population
    assert hasattr(population, "_id")
    assert hasattr(population, "experiment_id")
    assert hasattr(population, "gates")
    assert hasattr(population, "name")
    assert hasattr(population, "parent_id")
    assert hasattr(population, "terminal_gate_gid")
    assert hasattr(population, "unique_name")


@responses.activate
def test_update_population(experiment, population, populations):
    """Test that the .update() method makes the correct call. Does not test
    that the correct response is made; this should be done with an integration
    test.
    """
    # patch the mocked response with the correct values
    response = population._properties.copy()
    response.update({"name": "newname"})
    responses.add(
        responses.PATCH,
        base_url
        + "experiments/5d38a6f79fae87499999a74b/populations/{0}".format(population._id),
        json=response,
    )
    population.name = "newname"
    population.update()
    test_all_population_properties(population)
    assert json.loads(responses.calls[0].request.body) == population._properties


@responses.activate
def test_delete_population(experiment, population, populations):
    responses.add(
        responses.DELETE,
        base_url
        + "experiments/5d38a6f79fae87499999a74b/populations/{0}".format(population._id),
        status=204,
        body=b"",
    )
    delete_population = population.delete()
    assert delete_population is None
