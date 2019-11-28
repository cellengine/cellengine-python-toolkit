import os
import responses
import cellengine
from cellengine import _helpers


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")
# @responses.activate
# def test_list_fcsfile(experiment, files):
#     """Tests listing fcs files in an experiment"""
#     responses.add(responses.GET, base_url+"experiments/5d38a6f79fae87499999a74b/fcsfiles",
#                   json=files)
#     all_files = experiment.files
#     assert type(all_files) is list


def method_tester(res):
    """Generalize tests for common response fields"""
    assert res["_id"] == "5d38a6f79fae87499999a74b"
    assert res["name"] == "pytest_experiment"
    assert res["created"] == "2019-07-24T18:44:07.520Z"


@responses.activate
def test_base_get(experiments):
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    res = _helpers.base_get("experiments/5d38a6f79fae87499999a74b")
    method_tester(res)


@responses.activate
def test_base_create(experiments):
    """Test base_create for an instantiated data class response"""
    responses.add(
        responses.POST, base_url + "experiments", status=201, json=experiments[0]
    )
    res = _helpers.base_create(
        classname=cellengine.Experiment,
        url="experiments",
        expected_status=201,
        json={"name": "pytest_experiment"},
    )
    assert type(res) is cellengine.Experiment
    assert res.name == "pytest_experiment"


@responses.activate
def test_base_update(experiments):
    """Test doesn't actually update values, because we intercept the request."""
    responses.add(
        responses.PATCH,
        base_url + "experiments/5d64abe2ca9df61349ed8e78",
        json=experiments[0],
    )
    res = _helpers.base_update(
        "experiments/5d64abe2ca9df61349ed8e78",
        body={"name": "newname", "locked": True, "fullName": "Primity Bio"},
        classname=cellengine.Experiment,
    )
    assert type(res) is cellengine.Experiment
    assert res.name == "pytest_experiment"


@responses.activate
def test_base_list(fcsfiles):
    """Test one list query deeply"""
    experiment_id = "5d64abe2ca9df61349ed8e78"
    test_url = "experiments/{0}/{1}".format(experiment_id, "fcsfiles")
    responses.add(responses.GET, base_url + test_url, json=fcsfiles)
    res_list = _helpers.base_list(test_url, cellengine.FcsFile)
    res = res_list[0]
    assert type(res_list) is list
    assert [type(r) is cellengine.FcsFile for r in res_list]
    assert res._id == "5d64abe2ca9df61349ed8e79"
    assert res.filename == "Specimen_001_A12_A12.fcs"
    assert res.experiment_id == "5d64abe2ca9df61349ed8e78"
    assert res.event_count == 898


@responses.activate
def test_base_list_objects(experiments, compensations, fcsfiles, gates):
    """Test for all API list routes
    TODO: continue to fill in routes as classes are completed
    """

    # experiments
    responses.add(responses.GET, base_url + "experiments", json=experiments)
    response = _helpers.base_list("experiments", cellengine.Experiment)
    assert type(response) is list
    assert all([type(resp) is cellengine.Experiment for resp in response])

    # experiment.attachments

    # experiment.compensations
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/compensations",
        json=compensations,
    )
    response = _helpers.base_list(
        "experiments/5d38a6f79fae87499999a74b/compensations", cellengine.Compensation
    )
    assert type(response) is list
    assert all([type(resp) is cellengine.Compensation for resp in response])

    # experiment.fcsfiles
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/fcsfiles",
        json=fcsfiles,
    )
    response = _helpers.base_list(
        "experiments/5d38a6f79fae87499999a74b/fcsfiles", cellengine.FcsFile
    )
    assert type(response) is list
    assert all([type(resp) is cellengine.FcsFile for resp in response])

    # experiment.gates
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        json=gates,
    )
    response = _helpers.base_list(
        "experiments/5d38a6f79fae87499999a74b/gates", cellengine.Gate
    )
    assert type(response) is list
    assert type(response[0]) is cellengine.Gate
    assert all([type(resp) is cellengine.Gate for resp in response])

    # experiment.populations

    # experiment.scalesets
