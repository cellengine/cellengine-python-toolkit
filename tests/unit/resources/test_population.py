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


# @responses.activate
# def test_create_child_rectangle_gate(population, rectangle_gate):
#     """Test rectangle gate creation.

#     Note that the returned object may not have values that match the request.
#     This is because the returned object is built from a dict returned by a
#     pytest fixture (intercepted by `responses`), not by the CE API.
#     """
#     responses.add(
#         responses.POST,
#         base_url + "experiments/5d38a6f79fae87499999a74b/gates",
#         status=201,
#         json=rectangle_gate,
#     )
#     rectangle_gate = population.create_child_rectangle_gate(
#         x_channel="FSC-A",
#         y_channel="FSC-W",
#         name="my gate",
#         x1=60000,
#         x2=200000,
#         y1=75000,
#         y2=215000,
#     )
#     gate_tester(rectangle_gate)
#     request = json.loads(responses.calls[0].request.body)
#     assert request["parentPopulationId"] == population._id
#     assert request["experimentId"] == population.experiment_id
#     assert (
#         responses.calls[0].request.url
#         == base_url + "experiments/5d38a6f79fae87499999a74b/gates?createPopulation=True"
#     )


# @responses.activate
# def test_create_child_ellipse_gate(population, ellipse_gate):
#     responses.add(
#         responses.POST,
#         base_url + "experiments/5d38a6f79fae87499999a74b/gates",
#         status=201,
#         json=ellipse_gate,
#     )
#     ellipse_gate = population.create_child_ellipse_gate(
#         x_channel="FSC-A",
#         y_channel="FSC-W",
#         name="my gate",
#         x=259441.51377370575,
#         y=63059.462213950595,
#         angle=0,
#         major=120000,
#         minor=70000,
#     )
#     gate_tester(ellipse_gate)
#     request = json.loads(responses.calls[0].request.body)
#     assert request["parentPopulationId"] == population._id
#     assert request["experimentId"] == population.experiment_id
#     assert (
#         responses.calls[0].request.url
#         == base_url + "experiments/5d38a6f79fae87499999a74b/gates?createPopulation=True"
#     )


# @responses.activate
# def test_create_polygon_gate(population, polygon_gate):
#     responses.add(
#         responses.POST,
#         base_url + "experiments/5d38a6f79fae87499999a74b/gates",
#         status=201,
#         json=polygon_gate,
#     )
#     polygon_gate = population.create_child_polygon_gate(
#         x_channel="FSC-A",
#         y_channel="FSC-W",
#         name="my gate",
#         x_vertices=[1, 2, 3],
#         y_vertices=[4, 5, 6],
#     )
#     gate_tester(polygon_gate)
#     request = json.loads(responses.calls[0].request.body)
#     assert request["parentPopulationId"] == population._id
#     assert request["experimentId"] == population.experiment_id
#     assert (
#         responses.calls[0].request.url
#         == base_url + "experiments/5d38a6f79fae87499999a74b/gates?createPopulation=True"
#     )


# @responses.activate
# def test_create_range_gate(population, range_gate):
#     responses.add(
#         responses.POST,
#         base_url + "experiments/5d38a6f79fae87499999a74b/gates",
#         status=201,
#         json=range_gate,
#     )
#     range_gate = population.create_child_range_gate(
#         x_channel="FSC-A", name="my gate", x1=12.502, x2=95.102
#     )
#     gate_tester(range_gate)
#     request = json.loads(responses.calls[0].request.body)
#     assert request["parentPopulationId"] == population._id
#     assert request["experimentId"] == population.experiment_id
#     assert (
#         responses.calls[0].request.url
#         == base_url + "experiments/5d38a6f79fae87499999a74b/gates?createPopulation=True"
#     )


# @responses.activate
# def test_create_quadrant_gate(population, scalesets, quadrant_gate):
#     responses.add(
#         responses.GET,
#         base_url + "experiments/5d38a6f79fae87499999a74b/scalesets",
#         json=[scalesets],
#     )
#     responses.add(
#         responses.POST,
#         base_url + "experiments/5d38a6f79fae87499999a74b/gates",
#         status=201,
#         json=quadrant_gate,
#     )
#     quadrant_gate = population.create_child_quadrant_gate(
#         name="test_quadrant_gate",
#         x_channel="FSC-A",
#         y_channel="FSC-W",
#         x=160000,
#         y=200000,
#     )
#     gate_tester(quadrant_gate)
#     request = json.loads(responses.calls[1].request.body)
#     assert request["parentPopulationId"] == population._id
#     assert request["experimentId"] == population.experiment_id
#     assert (
#         responses.calls[1].request.url
#         == base_url + "experiments/5d38a6f79fae87499999a74b/gates?createPopulation=True"
#     )


# @responses.activate
# def test_create_split_gate(population, scalesets, split_gate):
#     responses.add(
#         responses.GET,
#         base_url + "experiments/5d38a6f79fae87499999a74b/scalesets",
#         json=[scalesets],
#     )
#     responses.add(
#         responses.POST,
#         base_url + "experiments/5d38a6f79fae87499999a74b/gates",
#         status=201,
#         json=split_gate,
#     )
#     split_gate = population.create_child_split_gate(
#         x_channel="FSC-A", name="my gate", x=160000, y=100000
#     )
#     gate_tester(split_gate)
#     request = json.loads(responses.calls[1].request.body)
#     assert request["parentPopulationId"] == population._id
#     assert request["experimentId"] == population.experiment_id
#     assert (
#         responses.calls[1].request.url
#         == base_url + "experiments/5d38a6f79fae87499999a74b/gates?createPopulation=True"
#     )
