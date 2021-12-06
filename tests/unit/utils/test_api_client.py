import re
import json
import pytest
import responses

from cellengine.resources.attachment import Attachment
from cellengine.resources.compensation import Compensation
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.gate import Gate
from cellengine.resources.plot import Plot
from cellengine.resources.population import Population
from cellengine.resources.scaleset import ScaleSet

EXP_ID = "5d38a6f79fae87499999a74b"
ATTACHMENT_ID = "5e3a5abf62c76b4f1b207b5b"
FCSFILE_ID = "5d64abe2ca9df61349ed8e7c"
COMPENSATION_ID = "5d64abe2ca9df61349ed8e95"
GATE_ID = "5d64abe2ca9df61349ed8e90"
POPULATION_ID = "5d3903529fae87499999a780"
STATISTICS_ID = "5d64abe2ca9df61349ed8e79"
SCALESET_ID = "5d38a6f79fae87499999a74c"


test_params = [
    # (json to return, endpoint, function to test, expected entity, function args)
    (Experiment, None, "get_experiments", None),
    (
        Experiment,
        EXP_ID,
        "get_experiment",
        {"_id": EXP_ID},
    ),
    (
        Experiment,
        EXP_ID,
        "get_experiment",
        {"name": "test_experiment"},
    ),
    (
        Attachment,
        EXP_ID,
        "get_attachments",
        {"experiment_id": EXP_ID},
    ),
    (
        bytes,
        EXP_ID,
        "download_attachment",
        {"experiment_id": EXP_ID, "_id": ATTACHMENT_ID},
    ),
    (
        bytes,
        EXP_ID,
        "download_attachment",
        {"experiment_id": EXP_ID, "name": "config.h"},
    ),
    (FcsFile, EXP_ID, "get_fcs_files", {"experiment_id": EXP_ID}),
    (
        FcsFile,
        EXP_ID,
        "get_fcs_file",
        {"experiment_id": EXP_ID, "_id": FCSFILE_ID},
    ),
    (
        FcsFile,
        EXP_ID,
        "get_fcs_file",
        {"experiment_id": EXP_ID, "name": "Specimen_001_A1_A01.fcs"},
    ),
    (Compensation, EXP_ID, "get_compensations", {"experiment_id": EXP_ID}),
    (
        Compensation,
        EXP_ID,
        "get_compensation",
        {"experiment_id": EXP_ID, "_id": COMPENSATION_ID},
    ),
    (
        Compensation,
        EXP_ID,
        "get_compensation",
        {"experiment_id": EXP_ID, "name": "some compensation"},
    ),
    (Gate, EXP_ID, "get_gates", {"experiment_id": EXP_ID}),
    (
        Gate,
        EXP_ID,
        "get_gate",
        {"experiment_id": EXP_ID, "_id": GATE_ID},
    ),
    (Population, EXP_ID, "get_populations", {"experiment_id": EXP_ID}),
    (
        Population,
        EXP_ID,
        "get_population",
        {"experiment_id": EXP_ID, "_id": POPULATION_ID},
    ),
    (
        Population,
        EXP_ID,
        "get_population",
        {"experiment_id": EXP_ID, "name": "test (UR)"},
    ),
]


@pytest.mark.parametrize("_type,exp_id,_func,kwargs", test_params)
@responses.activate
def test_should_get(
    client,
    ENDPOINT_BASE,
    attachments,
    compensations,
    experiments,
    fcs_files,
    gates,
    populations,
    _type,
    exp_id,
    _func,
    kwargs,
):
    """A general parametrized test for requesting entities from the APIClient.
    Loads resource fixtures (i.e. "attachments") from /tests/fixtures.

    Args:
        _type (Object): The resource type expected from the client.
        exp_id (str): The experiment_id associated with the resource.
        _func (str): The APIClient function to test. Evaluates as a function of the
            client, i.e. `get_attachment` -> `APIClient().get_attachment`
        kwargs (dict): Keyword arguments to pass to _func ->
            `APIClient()._func(**kwargs)`
    """
    entity = _get_entity_name(_func)
    endpoint = _make_endpoint(entity, exp_id, kwargs)
    json = eval(_get_fixture_item_or_list(entity, _func))

    if kwargs and "name" in kwargs:
        _mock_request_by_name(
            ENDPOINT_BASE, endpoint, exp_id, entity, kwargs["name"], json
        )
    else:
        _mock_request(ENDPOINT_BASE + endpoint, json)

    parametrized_func = getattr(client, _func)
    res = parametrized_func(**kwargs) if kwargs else parametrized_func()
    if type(res) is list:
        if entity == "gates":
            _assert_gate(res)
        else:
            assert all([type(r) is _type for r in res])
    else:
        if entity == "gates":
            _assert_gate(res)
        else:
            assert type(res) is _type


def _assert_gate(gate):
    if type(gate) is dict:
        assert "Gate" in gate["type"]
    elif type(gate) is list:
        assert all([str(g.__module__) == "cellengine.resources.gate" for g in gate])
    else:
        assert str(gate.__module__) == "cellengine.resources.gate"


def _get_entity_name(_func: str) -> str:
    entity = _func[_func.find("_") + 1 :]  # noqa: E203
    if entity[-1] != "s":
        entity += "s"
    return entity


def _get_fixture_item_or_list(entity: str, _func: str) -> str:
    """If _func is plural, return the name of a list fixture to be evaluated."""
    if _func[-1] == "s":
        return entity
    else:
        return entity + "[0]"


def _make_endpoint(entity, exp_id, kwargs):
    """Return the correct endpoint, given the entity name and experiment_id."""
    if "fcs" in entity:
        entity = "fcsfiles"
    if exp_id:
        if "experiment" in entity:
            endpoint = "/experiments"
        else:
            endpoint = f"/experiments/{exp_id}/{entity}"
        if "_id" in kwargs:
            endpoint = endpoint + f"/{kwargs['_id']}"
    else:
        endpoint = f"/{entity}"
    return endpoint


def _mock_request(url, json_response):
    responses.add(
        responses.GET,
        url,
        json=json_response,
    )


def _mock_request_by_name(base_url, endpoint, exp_id, entity, name, json_response):
    if "fcs" in entity:
        entity = "fcsfiles"
    if (entity == "fcsfiles") or (entity == "attachments"):
        query = "filename"
    else:
        query = "name"

    url = base_url + f"{endpoint}?query=eq({query},%22{name}%22)&limit=2"

    responses.add(
        responses.GET,
        url,
        json=json_response,
        match_querystring=True,
    )

    if entity == "experiments":
        id_url = f"{base_url}/experiments/{exp_id}"
    else:
        id_url = re.compile(
            base_url + "/experiments/" + exp_id + "/" + entity + r"/[a-f0-9]{24}$", re.I
        )

    responses.add(
        responses.GET,
        id_url,
        json=json_response,
    )


@responses.activate
def test_should_get_plot(client, ENDPOINT_BASE):
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/plot",
        match_querystring=False,
    )
    plot = client.get_plot(EXP_ID, FCSFILE_ID, "FSC-A", "FSC-H", "dot")
    assert type(plot) is Plot


@responses.activate
def test_should_get_scaleset(client, ENDPOINT_BASE, scalesets):
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/scalesets",
        json=[scalesets],
    )
    s = client.get_scaleset(EXP_ID)
    assert type(s is ScaleSet)
    assert s._id == SCALESET_ID


@responses.activate
def test_should_get_statistics(client, ENDPOINT_BASE, statistics):
    responses.add(
        responses.POST,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/bulkstatistics",
        json=statistics,
    )

    expected_query_body = {
        "statistics": "mean",
        "q": 1,
        "channels": "FSC-A",
        "annotations": False,
        "compensationId": "some id",
        "fcsFileIds": "some file id",
        "format": "json",
        "layout": "medium",
        "percentOf": "PARENT",
        "populationIds": "some population id",
    }
    client.get_statistics(
        EXP_ID,
        "mean",
        "FSC-A",
        q=1,
        compensation_id="some id",
        fcs_file_ids="some file id",
        format="json",
        layout="medium",
        percent_of="PARENT",
        population_ids="some population id",
    )
    assert set(expected_query_body) == set(json.loads(responses.calls[0].request.body))
