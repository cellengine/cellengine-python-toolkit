import json
import pytest
import responses

from cellengine.resources.population import Population


EXP_ID = "5d38a6f79fae87499999a74b"


@pytest.fixture(scope="module")
def population(client, populations):
    return Population.from_dict(populations[0])


def population_tester(population):
    assert type(population) is Population
    assert hasattr(population, "_id")
    assert hasattr(population, "experiment_id")
    assert hasattr(population, "gates")
    assert hasattr(population, "name")
    assert hasattr(population, "parent_id")
    assert (
        hasattr(population, "terminal_gate_gid")
        and len(getattr(population, "terminal_gate_gid")) == 24
    )
    assert hasattr(population, "unique_name")


@responses.activate
def test_should_get_population(ENDPOINT_BASE, population, populations):
    responses.add(
        responses.GET,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/populations/{population._id}",
        json=populations[0],
    )
    pop = Population.get(EXP_ID, population._id)
    population_tester(pop)


@responses.activate
def test_should_post_population(ENDPOINT_BASE, population, populations):
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/populations",
        json=populations[0],
    )
    payload = populations[0].copy()
    pop = Population.create(EXP_ID, payload)
    population_tester(pop)


@responses.activate
def test_update_population(ENDPOINT_BASE, population):
    """Test that the .update() method makes the correct call. Does not test
    that the correct response is made; this should be done with an integration
    test.
    """
    # patch the mocked response with the correct values
    response = population.to_dict().copy()
    response.update({"name": "newname"})
    responses.add(
        responses.PATCH,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/populations/{population._id}",
        json=response,
    )
    population.name = "newname"
    population.update()
    population_tester(population)
    assert (
        json.loads(responses.calls[0].request.body)  # type: ignore
        == population.to_dict()
    )


@responses.activate
def test_delete_population(ENDPOINT_BASE, population):
    responses.add(
        responses.DELETE,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/populations/{population._id}",
        status=204,
        body=b"",
    )
    delete_population = population.delete()
    assert delete_population is None
