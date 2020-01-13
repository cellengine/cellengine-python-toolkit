import os
import responses
import cellengine
from cellengine.utils import loader

# TODO: pull the double-responses from a name request into a fixture
#       see the `responses` documentation on pytest fixtures


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@responses.activate
def test_lru_cache(client, experiments):
    """Test to see if the LRU cache added hits. Multiple queries of the same
    object should add hits and new queries should add a miss."""
    loader.by_name.cache_clear()

    responses.add(responses.GET, base_url + "experiments", json=experiments[0])
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    exp1 = client.get_experiment(name="test_experiment")
    assert loader.by_name.cache_info().misses == 1

    responses.add(responses.GET, base_url + "experiments", json=experiments[0])
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    exp1 = client.get_experiment(name="test_experiment")
    assert loader.by_name.cache_info().misses == 1
    assert loader.by_name.cache_info().hits == 1

    responses.add(responses.GET, base_url + "experiments", json=experiments[1])
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=experiments[1],
    )
    exp2 = client.get_experiment(name="test_experiment-1")
    assert loader.by_name.cache_info().misses == 2


@responses.activate
def test_lru_cache_paths(client, experiments, fcsfiles, experiment):
    """Test whether the cache returns a url with a name query on the first
    request and then an ID on the second request."""
    loader.by_name.cache_clear()

    responses.add(responses.GET, base_url + "experiments", json=experiments[0])
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )

    exp = client.get_experiment(name="test_experiment")
    assert (
        responses.calls[0].request.url
        == base_url + "experiments?query=eq(name,%22test_experiment%22)&limit=2"
    )

    responses.add(responses.GET, base_url + "experiments", json=experiments[0])
    exp_copy = client.get_experiment(name="test_experiment")
    assert (
        responses.calls[1].request.url
        == base_url + "experiments/5d38a6f79fae87499999a74b"
    )

    responses.add(responses.GET, base_url + "experiments", json=[experiments[1]])
    responses.add(
        responses.GET,
        base_url + "experiments/5d5faa686d24fd0bf35129b1",
        json=experiments[1],
    )
    different_exp = client.get_experiment(name="pytest_experiment")
    assert (
        responses.calls[2].request.url
        == base_url + "experiments/5d38a6f79fae87499999a74b"
    )


@responses.activate
def test_different_item_cache_accessor(client, experiments, fcsfiles):
    """Test to see if the LRU cache adds hits. Multiple queries of the same
    object should add hits and new queries should add a miss.

    Multiple queries of files of the same name in different experiments should
    register as different queries."""
    loader.by_name.cache_clear()

    responses.add(
        responses.GET,
        base_url + "experiments?query=eq(name,%22test_experiment%22)&limit=2",
        json=experiments[0],
        match_querystring=True,
    )
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    exp1 = client.get_experiment(name="test_experiment")
    assert loader.by_name.cache_info().misses == 1

    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/fcsfiles",
        json=fcsfiles[0],
    )
    responses.add(
        responses.GET,
        base_url
        + "experiments/5d38a6f79fae87499999a74b/fcsfiles/5d64abe2ca9df61349ed8e79",
        json=fcsfiles[0],
    )
    file1 = exp1.get_fcsfile(name="Specimen_001_A12_A12.fcs")
    assert loader.by_name.cache_info().misses == 2

    responses.add(
        responses.GET,
        base_url + "experiments?query=eq(name,%22test_experiment-1%22)&limit=2",
        json=experiments[1],
        match_querystring=True,
    )
    responses.add(
        responses.GET,
        base_url + "experiments/5d5faa686d24fd0bf35129b1",
        json=experiments[1],
    )
    exp2 = client.get_experiment(name="test_experiment-1")
    assert loader.by_name.cache_info().misses == 3

    responses.add(
        responses.GET,
        base_url + "experiments/5d5faa686d24fd0bf35129b1/fcsfiles",
        json=fcsfiles[1],
    )
    responses.add(
        responses.GET,
        base_url
        + "experiments/5d5faa686d24fd0bf35129b1/fcsfiles/5d64abe2ca9df61349ed8e7a",
        json=fcsfiles[1],
    )
    file2 = exp2.get_fcsfile(name="Specimen_001_A12_A12.fcs")
    assert (
        loader.by_name.cache_info().misses == 4
    )  # not 3 because this is a different experiment

    assert file1._id != file2._id


@responses.activate
def test_global_cache_accessor(client, experiments):
    loader.by_name.cache_clear()
    assert cellengine.cache_info().misses == 0
    assert loader.by_name.cache_info().misses == 0

    responses.add(responses.GET, base_url + "experiments", json=experiments[0])
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    exp1 = client.get_experiment(name="test_experiment")
    assert cellengine.cache_info().misses == 1
    assert loader.by_name.cache_info().misses == 1

    cellengine.clear_cache()
    assert cellengine.cache_info().misses == 0
    assert loader.by_name.cache_info().misses == 0
