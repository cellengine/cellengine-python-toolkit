import responses


@responses.activate
def test_lru_cache(ENDPOINT_BASE, client, experiments):
    """Test to see if the LRU cache added hits. Multiple queries of the same
    object should add hits and new queries should add a miss."""
    client.cache_clear()

    responses.add(responses.GET, ENDPOINT_BASE + "/experiments", json=experiments[0])
    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    client.get_experiment(name="test_experiment")
    assert client.cache_info().misses == 1

    responses.add(responses.GET, ENDPOINT_BASE + "/experiments", json=experiments[0])
    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    client.get_experiment(name="test_experiment")
    assert client.cache_info().misses == 1
    assert client.cache_info().hits == 1

    responses.add(responses.GET, ENDPOINT_BASE + "/experiments", json=experiments[1])
    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b",
        json=experiments[1],
    )
    client.get_experiment(name="test_experiment-1")
    assert client.cache_info().misses == 2


@responses.activate
def test_lru_cache_paths(ENDPOINT_BASE, client, experiments, fcsfiles, experiment):
    """Test whether the cache returns a url with a name query on the first
    request and then an ID on the second request."""
    client.cache_clear()

    responses.add(responses.GET, ENDPOINT_BASE + "/experiments", json=experiments[0])
    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )

    client.get_experiment(name="test_experiment")
    assert (
        responses.calls[0].request.url
        == ENDPOINT_BASE + "/experiments?query=eq(name,%22test_experiment%22)&limit=2"
    )

    responses.add(responses.GET, ENDPOINT_BASE + "/experiments", json=experiments[0])
    client.get_experiment(name="test_experiment")
    assert (
        responses.calls[1].request.url
        == ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b"
    )

    responses.add(responses.GET, ENDPOINT_BASE + "/experiments", json=[experiments[1]])
    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d5faa686d24fd0bf35129b1",
        json=experiments[1],
    )
    client.get_experiment(name="pytest_experiment")
    assert (
        responses.calls[2].request.url
        == ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b"
    )


@responses.activate
def test_different_item_cache_accessor(ENDPOINT_BASE, client, experiments, fcsfiles):
    """Test to see if the LRU cache adds hits. Multiple queries of the same
    object should add hits and new queries should add a miss.

    Multiple queries of files of the same name in different experiments should
    register as different queries."""
    client.cache_clear()

    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments?query=eq(name,%22test_experiment%22)&limit=2",
        json=experiments[0],
        match_querystring=True,
    )
    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    exp1 = client.get_experiment(name="test_experiment")
    assert client.cache_info().misses == 1

    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b/fcsfiles",
        json=fcsfiles[0],
    )
    responses.add(
        responses.GET,
        ENDPOINT_BASE
        + "/experiments/5d38a6f79fae87499999a74b/fcsfiles/5d64abe2ca9df61349ed8e79",
        json=fcsfiles[0],
    )
    file1 = exp1.get_fcsfile(name="Specimen_001_A12_A12.fcs")
    assert client.cache_info().misses == 2

    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments?query=eq(name,%22test_experiment-1%22)&limit=2",
        json=experiments[1],
        match_querystring=True,
    )
    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d5faa686d24fd0bf35129b1",
        json=experiments[1],
    )
    exp2 = client.get_experiment(name="test_experiment-1")
    assert client.cache_info().misses == 3

    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d5faa686d24fd0bf35129b1/fcsfiles",
        json=fcsfiles[1],
    )
    responses.add(
        responses.GET,
        ENDPOINT_BASE
        + "/experiments/5d5faa686d24fd0bf35129b1/fcsfiles/5d64abe2ca9df61349ed8e7a",
        json=fcsfiles[1],
    )
    file2 = exp2.get_fcsfile(name="Specimen_001_A12_A12.fcs")
    assert (
        client.cache_info().misses == 4
    )  # not 3 because this is a different experiment

    assert file1._id != file2._id


@responses.activate
def test_global_cache_accessor(ENDPOINT_BASE, client, experiments):
    client.cache_clear()
    assert client.cache_info().misses == 0
    assert client.cache_info().misses == 0

    responses.add(responses.GET, ENDPOINT_BASE + "/experiments", json=experiments[0])
    responses.add(
        responses.GET,
        ENDPOINT_BASE + "/experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    client.get_experiment(name="test_experiment")
    assert client.cache_info().misses == 1
    assert client.cache_info().misses == 1

    client.cache_clear()
    assert client.cache_info().misses == 0
    assert client.cache_info().misses == 0
