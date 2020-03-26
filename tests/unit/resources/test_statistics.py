import os
import json
import pytest
import pandas
import responses
from requests.exceptions import RequestException

import cellengine
from cellengine.resources.statistics import get_statistics

base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@pytest.fixture(scope="module")
def statistic_response(experiment, statistics):
    return statistics


@responses.activate
def test_object_should_request_all_properties(experiment, statistic_response):
    responses.add(
        responses.POST,
        base_url + "experiments/{}/bulkstatistics".format(experiment._id),
        json=statistic_response,
    )

    body = "statistics=mean&q=1&channels=FSC-A&annotations=False&compensationId=some+id&fcsFileIds=some+file+id&format=json&layout=medium&percentOf=PARENT&populationIds=some+population+id"
    stats = get_statistics(
        experiment._id,
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

    assert responses.calls[0].request.body == body


@pytest.mark.vcr()
def test_should_get_list_of_stats():
    methods_to_get = ["mean", "mad", "stddev"]
    stats = get_statistics("5e4fcb98bdd7ea051d703652", methods_to_get, "FSC-A")
    assert all([method in stats[0].keys() for method in methods_to_get])


@pytest.mark.vcr()
def test_should_get_list_of_stats():
    channels_to_get = ["FSC-A", "FSC-H"]
    stats = get_statistics("5e4fcb98bdd7ea051d703652", "mean", channels_to_get)
    assert any([channels_to_get[0] in stat["channel"] for stat in stats])
    assert any([channels_to_get[1] in stat["channel"] for stat in stats])


@pytest.mark.vcr()
def test_quantile_should_require_q():
    with pytest.raises(RequestException):
        get_statistics("5e4fcb98bdd7ea051d703652", "quantile", "FSC-A")

    # passes with q set
    get_statistics("5e4fcb98bdd7ea051d703652", "quantile", "FSC-A", q=0.75)


@pytest.mark.vcr()
def test_should_get_every_statistics_type():
    methods = [
        "mean",
        "median",
        "mad",
        "geometricMean",
        "eventCount",
        "cv",
        "stddev",
        "percent",
    ]
    for method in methods:
        stats = get_statistics("5e4fcb98bdd7ea051d703652", method, "FSC-A")
        assert [method in stat.keys() for stat in stats]


@pytest.mark.vcr()
def test_should_get_formatted_csv():
    stats = get_statistics(
        "5e4fcb98bdd7ea051d703652", "mean", "FSC-A", format="csv", layout="short-wide"
    )
    # count rows by row delimiter:
    assert type(stats.find("\r")) == int


@responses.activate
def test_should_return_pandas_dataframe(statistic_response):
    responses.add(
        responses.POST,
        base_url + "experiments/5e4fcb98bdd7ea051d703653/bulkstatistics",
        json=statistic_response,
    )
    stats = get_statistics("5e4fcb98bdd7ea051d703653", "mean", "FSC-A", format="pandas")
    properties = [
        "fcsFileId",
        "filename",
        "populationId",
        "population",
        "uniquePopulationName",
        "parentPopulation",
        "parentPopulationId",
    ]
    assert all(prop in stats.columns.to_list() for prop in properties)
