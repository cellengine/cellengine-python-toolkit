import os
import pytest
import responses
from tests.unit.resources.test_population import (  # noqa: F401
    population_tester,
    population,
)


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
