import os
import json
import responses
import cellengine
from cellengine.utils import helpers


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@responses.activate
def test_update_experiment(experiments):
    """Tests updating experiment params"""
    experiment = cellengine.Experiment(experiments[0])
    response = experiments[0].copy()
    response.update({"name": "new name"})
    responses.add(
        responses.PATCH,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=response,
    )
    assert experiment.name == "pytest_experiment"
    experiment.name = "new name"
    experiment.update()
    assert experiment.name == "new name"
    assert json.loads(responses.calls[0].request.body) == experiment._properties


@responses.activate
def test_list_fcsfile(experiment, fcsfiles):
    """Tests listing fcs files in an experiment"""
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/fcsfiles",
        json=fcsfiles,
    )
    all_files = experiment.files
    assert type(all_files) is list
    assert all([type(file) is cellengine.FcsFile for file in all_files])


@responses.activate
def test_list_populations(experiment, populations):
    """Tests listing files in an experiment"""
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/populations",
        json=populations,
    )
    all_populations = experiment.populations
    assert type(all_populations) is list
    assert all(
        [type(population) is cellengine.Population for population in all_populations]
    )


@responses.activate
def test_list_compensations(experiment, compensations):
    """Tests listing compensations in an experiment"""
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/compensations",
        json=compensations,
    )
    all_compensations = experiment.compensations
    assert type(all_compensations) is list
    assert all(
        [
            type(compensation) is cellengine.Compensation
            for compensation in all_compensations
        ]
    )


@responses.activate
def test_list_gates(experiment, gates):
    """Tests listing gates in an experiment"""
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/gates",
        json=gates,
    )
    all_gates = experiment.gates
    assert type(all_gates) is list
    assert all([type(gate) is cellengine.Gate for gate in all_gates])


@responses.activate
def test_all_experiment_properties(experiment):
    assert type(experiment._properties) is dict
    assert experiment._id == "5d38a6f79fae87499999a74b"
    assert experiment.name == "pytest_experiment"
    assert experiment.comments == [{"insert": "\xa0\xa0\xa0First 12 of 96 files\n\n"}]
    assert experiment.updated == helpers.timestamp_to_datetime(
        "2019-08-29T14:40:58.566Z"
    )
    assert experiment.deep_updated == helpers.timestamp_to_datetime(
        "2019-10-15T09:58:38.224Z"
    )
    assert experiment.deleted is None
    assert experiment.public is False
    assert experiment.uploader == {
        "_id": "5d366077a1789f7d6653075c",
        "username": "gegnew",
        "email": "g.egnew@gmail.com",
        "firstName": "Gerrit",
        "lastName": "Egnew",
        "fullName": "Gerrit Egnew",
        "id": "5d366077a1789f7d6653075c",
    }
    assert experiment.primary_researcher == {
        "_id": "5d366077a1789f7d6653075c",
        "username": "gegnew",
        "email": "g.egnew@gmail.com",
        "firstName": "Gerrit",
        "lastName": "Egnew",
        "fullName": "Gerrit Egnew",
        "id": "5d366077a1789f7d6653075c",
    }
    assert experiment.active_compensation == 0
    assert experiment.locked is False
    # assert experiment.clone_source_experiment  # does not exist for this exp
    # assert experiment.revision_source_experiment  # does not exist for this exp
    assert experiment.revisions == []
    assert experiment.per_file_compensations_enabled is False
    assert experiment.tags == []
    assert experiment.annotation_name_order == []
    assert experiment.annotation_table_sort_columns == []
    assert experiment.permissions == []
    assert experiment.created == helpers.timestamp_to_datetime(
        "2019-07-24T18:44:07.520Z"
    )


@responses.activate
def test_get_statistics(experiment):
    """Tests getting statistics for an experiment"""
    responses.add(
        responses.POST,
        base_url + "experiments/{}/bulkstatistics".format(experiment._id),
        json={"some": "json"},
    )
    body = "statistics=mean&channels=FSC-A&annotations=False&format=json"
    experiment.get_statistics("mean", "FSC-A")
    assert responses.calls[0].request.body == body
