from cellengine.utils.api_client.APIClient import APIClient
from cellengine.utils import converter
import json
from numpy import array
import pytest
import responses
from pandas import DataFrame
from cellengine.resources.compensation import Compensation


EXP_ID = "5d38a6f79fae87499999a74b"


@pytest.fixture(scope="function")
def compensation(ENDPOINT_BASE, client, compensations):
    comp = compensations[0]
    comp.update({"experimentId": EXP_ID})
    return converter.structure(comp, Compensation)


def properties_tester(comp):
    assert type(comp) is Compensation
    assert hasattr(comp, "_id")
    assert hasattr(comp, "name")
    assert hasattr(comp, "experiment_id")
    assert hasattr(comp, "channels")
    assert hasattr(comp, "N")
    assert comp.N == len(comp.dataframe)
    assert hasattr(comp, "dataframe")
    assert type(comp.dataframe) is DataFrame
    assert all(comp.dataframe.index == comp.channels)
    assert hasattr(comp, "apply")
    assert hasattr(comp, "dataframe_as_html")


def test_compensation_properties(ENDPOINT_BASE, compensation):
    properties_tester(compensation)


@responses.activate
def test_should_post_compensation(client, ENDPOINT_BASE, compensations):
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/compensations",
        json=compensations[0],
    )
    comp = Compensation(None, EXP_ID, "test_comp", ["a", "b"], [1, 0, 0, 1])
    comp = client.create(comp)
    properties_tester(comp)


@responses.activate
def test_should_create_compensation(client, ENDPOINT_BASE, compensations):
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/compensations",
        json=compensations[0],
    )
    comp = client.create_compensation(EXP_ID, ["a", "b"], "test-comp", [1, 0, 0, 1])
    properties_tester(comp)


@responses.activate
def test_should_delete_compensation(ENDPOINT_BASE, compensation):
    responses.add(
        responses.DELETE,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/compensations/{compensation._id}",
    )
    deleted = compensation.delete()
    assert deleted is None


@responses.activate
def test_should_update_compensation(ENDPOINT_BASE, compensation):
    """Test that the .update() method makes the correct call. Does not test
    that the correct response is made; this should be done with an integration
    test.
    """
    # patch the mocked response with the correct values
    response = converter.unstructure(compensation)
    response.update({"name": "newname"})
    responses.add(
        responses.PATCH,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/compensations/{compensation._id}",
        json=response,
    )
    compensation.name = "newname"
    compensation.update()
    properties_tester(compensation)
    assert json.loads(responses.calls[0].request.body) == response


def test_create_from_spill_string(spillstring):
    comp = Compensation.from_spill_string(spillstring)
    spillstring.replace
    assert type(comp) is Compensation

    assert comp.channels == [
        "Ax488-A",
        "PE-A",
        "PE-TR-A",
        "PerCP-Cy55-A",
        "PE-Cy7-A",
        "Ax647-A",
        "Ax700-A",
        "Ax750-A",
        "PacBlu-A",
        "Qdot525-A",
        "PacOrange-A",
        "Qdot605-A",
        "Qdot655-A",
        "Qdot705-A",
    ]
