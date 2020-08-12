import os
import json
import pytest
import responses

from cellengine.resources.population import Population
from cellengine.utils.complex_population_builder import ComplexPopulationBuilder

EXP_ID = "5d38a6f79fae87499999a74b"
ID1 = "5f1178fc2c50066876d24aca"
ID2 = "5f1178fc2c50066876d24acb"
ID3 = "5f1178fc2c50066876d24acc"
ID4 = "5f1178fc2c50066876d24acd"
ID5 = "5f1178fc2c50066876d24ace"
ID6 = "5f1178fc2c50066876d24acf"
ID7 = "5f1178fc2c50066876d24acg"


@responses.activate
def test_create_complex_population_basic(ENDPOINT_BASE, experiment, gates, populations):
    with pytest.raises(NotImplementedError):
        responses.add(
            responses.POST,
            f"{ENDPOINT_BASE}/experiments/{EXP_ID}/populations",
            json=populations[0],
            status=201,
        )
        complex_pop = experiment.create_population(
            population=ComplexPopulationBuilder("pop_name")
            .And([ID1, ID2])
            .Not(ID3)
            .build()
        )
        # TODO: assert correct body upon implementation


def test_should_build_query_from_string_or_list():
    expected_output = {
        "name": "pop_name",
        "gates": json.dumps({"$and": ["1"]}),
        "parentId": None,
        "terminalGateGid": None,
    }
    assert ComplexPopulationBuilder("pop_name").And("1").build() == expected_output
    assert ComplexPopulationBuilder("pop_name").And(["1"]).build() == expected_output


def test_should_build_complex_population_query_by_chaining():
    complex_pop = (
        ComplexPopulationBuilder("pop_name")
        .And([ID1, ID2])
        .Or([ID3])
        # drop one function to check that None is not included
        # .Not([ID4])
        .Xor([ID5, ID6, ID7])
    )
    assert complex_pop.build() == {
        "name": "pop_name",
        "gates": json.dumps(
            {
                "$and": [
                    ID1,
                    ID2,
                    {"$or": [ID3]},
                    # {"$not": [ID4]},
                    {"$xor": [ID5, ID6, ID7]},
                ]
            }
        ),
        "parentId": None,
        "terminalGateGid": None,
    }


def test_should_build_complex_population_query():
    complex_pop = ComplexPopulationBuilder("pop_name")
    complex_pop.And(["1", "2"])
    assert complex_pop.build() == {
        "name": "pop_name",
        "gates": json.dumps({"$and": ["1", "2",]}),
        "parentId": None,
        "terminalGateGid": None,
    }
    complex_pop.Or(["3"])
    assert complex_pop.build() == {
        "name": "pop_name",
        "gates": json.dumps({"$and": ["1", "2", {"$or": ["3"]},]}),
        "parentId": None,
        "terminalGateGid": None,
    }
    complex_pop.Not(["4"])
    assert complex_pop.build() == {
        "name": "pop_name",
        "gates": json.dumps({"$and": ["1", "2", {"$or": ["3"]}, {"$not": ["4"]},]}),
        "parentId": None,
        "terminalGateGid": None,
    }
    complex_pop.Xor(["5", "6", "7"])
    assert complex_pop.build() == {
        "name": "pop_name",
        "gates": json.dumps(
            {
                "$and": [
                    "1",
                    "2",
                    {"$or": ["3"]},
                    {"$not": ["4"]},
                    {"$xor": ["5", "6", "7"]},
                ]
            }
        ),
        "parentId": None,
        "terminalGateGid": None,
    }


def test_should_append_new_query():
    complex_pop = ComplexPopulationBuilder("pop_name").And(["1", "2"])
    assert complex_pop.build() == {
        "name": "pop_name",
        "gates": json.dumps({"$and": ["1", "2",]}),
        "parentId": None,
        "terminalGateGid": None,
    }
    complex_pop.And(["3"])
    assert complex_pop.build() == {
        "name": "pop_name",
        "gates": json.dumps({"$and": ["1", "2", "3"]}),
        "parentId": None,
        "terminalGateGid": None,
    }
