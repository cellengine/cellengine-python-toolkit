import os
import pytest
import responses

from cellengine.resources.population import Population


def population_tester(population):
    assert type(population._properties) is dict
    assert type(population) is Population
    assert hasattr(population, "_id")
    assert hasattr(population, "experiment_id")
    assert hasattr(population, "gates")
    assert hasattr(population, "name")
    assert hasattr(population, "parent_id")
    assert hasattr(population, "terminal_gate_gid")
    assert hasattr(population, "unique_name")


@responses.activate
def test_create_complex_population_basic(ENDPOINT_BASE, experiment, gates, populations):
    with pytest.raises(NotImplementedError):
        responses.add(
            responses.POST,
            ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b/populations",
            json=populations[0],
            status=201,
        )
        complex_pop = experiment.create_complex_population(
            base_gate=gates[0]["_id"],
            name="complex",
            gates={
                "$and": [
                    gates[1]["_id"],
                    gates[2]["_id"],
                    {"$or": [gates[3]["_id"], gates[4]["_id"]]},
                ]
            },
        )

        population_tester(complex_pop)
