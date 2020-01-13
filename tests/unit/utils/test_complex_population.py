import os
import responses
from tests.unit.resources.test_population import test_all_population_properties, population
from cellengine.utils.complex_population_creator import And

base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@responses.activate
def test_create_complex_population_basic(experiment, gates, populations):
    responses.add(
        responses.POST,
        base_url + "experiments/5d38a6f79fae87499999a74b/populations",
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

    test_all_population_properties(complex_pop)
