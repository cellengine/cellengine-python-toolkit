import os
import responses
import cellengine


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


def test_client(client):
    assert client.username == "gegnew"
    assert client.password == "testpass1"


@responses.activate
def test_list_experiments(client, experiments):
    responses.add(responses.GET, base_url + "experiments", json=experiments)
    all_experiments = client.experiments
    assert type(all_experiments) is list
    assert all([type(exp) is cellengine.Experiment for exp in all_experiments])


@responses.activate
def test_get_experiment(client, experiments):
    """Tests getting an experiment from api and existence of attributes."""
    responses.add(
        responses.GET,
        base_url + "experiments",
        json=experiments[0],
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    exp = client.get_experiment(name="test_experiment")
    assert type(exp._properties) is dict
    assert hasattr(exp, "name")
    assert hasattr(exp, "_id")
    assert hasattr(exp, "comments")
    assert hasattr(exp, "updated")
    assert hasattr(exp, "deep_updated")
    assert hasattr(exp, "deleted")
    assert hasattr(exp, "public")
    assert hasattr(exp, "uploader")
    assert hasattr(exp, "primary_researcher")
    assert hasattr(exp, "active_compensation")
    assert hasattr(exp, "locked")
    assert hasattr(exp, "clone_source_experiment")
    assert hasattr(exp, "revision_source_experiment")
    assert hasattr(exp, "revisions")
    assert hasattr(exp, "per_file_compensations_enabled")
    assert hasattr(exp, "tags")
    assert hasattr(exp, "annotation_name_order")
    assert hasattr(exp, "annotation_table_sort_columns")
    assert hasattr(exp, "permissions")
    assert hasattr(exp, "created")
    assert hasattr(exp, "delete_gates")
    assert hasattr(exp, "create_rectangle_gate")
    assert hasattr(exp, "create_polygon_gate")
    assert hasattr(exp, "create_ellipse_gate")
    assert hasattr(exp, "create_range_gate")
    assert hasattr(exp, "create_split_gate")
    assert hasattr(exp, "create_quadrant_gate")
