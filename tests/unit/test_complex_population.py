import os
import responses
from test_population import test_all_population_properties, population
from cellengine.complex_population_creator import And

base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


# @responses.activate
# def test_create_complex_population(experiment, gates, populations):
#     responses.add(
#         responses.GET,
#         base_url + "experiments/5d38a6f79fae87499999a74b/gates",
#         json=gates,
#     )
#     responses.add(
#         responses.POST,
#         base_url + "experiments/5d38a6f79fae87499999a74b/populations",
#         status=201,
#         json=populations[0],
#     )
#     exp_gates = experiment.gates
#     base_gate = exp_gates[0]
#     and_gates = exp_gates[1:2]
#     not_gates = exp_gates[2:3]
#     or_gates = exp_gates[4]
#     xor_gates = exp_gates[5]
#     complex_pop = experiment.create_complex_population(
#         name="complex_pop",
#         base_gate=base_gate,
#         and_gates=and_gates,
#         not_gates=not_gates,
#         or_gates=or_gates,
#         xor_gates=xor_gates,
#     )
# test_all_population_properties(complex_pop)


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


# def test_create_complex_population_with_and_builder(experiment, gates):
#     complex_pop = experiment.create_complex_population(
#         gates[0]["_id"], "complex", And(gates[1]["_id"])
#     )
#     test_all_population_properties(complex_pop)


# def test_create_complex_population_with_object_builders(experiment, gates):
#     complex_pop = experiment.create_complex_population(
#         gates[0]["_id"], "complex", And(gates[1]["_id"], Or(gates[2]["_id"]))
#     )
#     test_all_population_properties(complex_pop)
