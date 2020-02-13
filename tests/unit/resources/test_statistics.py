import os
import json
import pytest
import pandas
import responses
from requests.exceptions import RequestException
import cellengine
from cellengine.resources.statistics import StatisticRequest
from cellengine.utils.helpers import snake_to_camel

base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")

client = cellengine.Client("gegnew", "^w^A7kpB$2sezF")


@pytest.fixture(scope="module")
def statistic_response(experiment, statistics):
    # with responses.RequestsMock() as resps:
    #     resps.add(
    #         responses.GET,
    #         base_url + "experiments/5d38a6f79fae87499999a74b/bulkstatistics",
    #         json=statistics,
    #     )
    return statistics


def statistics_tester(res):
    assert type(res) is list
    properties = [
        'fcsFileId',
        'filename',
        'populationId',
        'population',
        'uniquePopulationName',
        'parentPopulation',
        'parentPopulationId',
    ]
    for item in res:
        assert all(prop in item.keys() for prop in properties)


@responses.activate
def test_object_should_request_all_properties(experiment, statistic_response):
    params = {
        "statistics": None,
        "q": None,
        "channels": [],
        "annotations": False,
        "compensationId": None,
        "fcsFileIds": None,
        "format": "json",
        "layout": None,
        "percentOf": None,
        "populationIds": None,
    }
    responses.add(
        responses.POST, base_url + "experiments/5e4fcb98bdd7ea051d703652/bulkstatistics", json=statistic_response
    )
    s = StatisticRequest("5e4fcb98bdd7ea051d703652")
    s.q = 1
    s.channels.append("FSC-A")
    s.annotations = False
    s.compensation_id = "some id"
    s.fcs_file_ids = "some file id"
    s.format = "json"
    s.layout = "medium"
    s.percent_of = "PARENT"
    s.population_ids = "some population id"

    s.get("mean")

    body = "statistics=mean&q=1&channels=FSC-A&annotations=False&compensationId=some+id&fcsFileIds=some+file+id&format=json&layout=medium&percentOf=PARENT&populationIds=some+population+id"
    assert responses.calls[0].request.body == body
    s.cache_clear()


def test_should_get_list_of_stats(statistic_response):
    s = StatisticRequest("5e4fcb98bdd7ea051d703652")
    s.channels = ['FSC-A']
    methods_to_get = ["mean", "mad", "stddev"]
    stats = s.get(methods_to_get)
    assert all([method in stats[0].keys() for method in methods_to_get])
    s.cache_clear()


def test_should_get_stats_when_called_second_time_without_method(statistic_response):
    s = StatisticRequest("5e4fcb98bdd7ea051d703652")
    s.get("mean")
    stats = s.get()
    statistics_tester(stats)
    s.cache_clear()


@responses.activate
def test_should_cache_same_request(statistic_response):
    s = StatisticRequest("5e4fcb98bdd7ea051d703652")
    responses.add(
        responses.POST, base_url + "experiments/5e4fcb98bdd7ea051d703652/bulkstatistics", json=statistic_response
    )
    s.get("mean")
    s.get("mean")
    assert len(responses.calls) == 1
    s.cache_clear()


@responses.activate
def test_should_not_cache_different_request(statistic_response):
    s = StatisticRequest("5e4fcb98bdd7ea051d703652")
    responses.add(
        responses.POST, base_url + "experiments/5e4fcb98bdd7ea051d703652/bulkstatistics", json=statistic_response
    )
    s.get("mean")
    s.get("mad")
    assert len(responses.calls) == 2
    s.cache_clear()


@responses.activate
def test_should_not_cache_when_params_are_changed(statistic_response):
    s = StatisticRequest("5e4fcb98bdd7ea051d703652")
    responses.add(
        responses.POST, base_url + "experiments/5e4fcb98bdd7ea051d703652/bulkstatistics", json=statistic_response
    )
    s.channels = ['FSC-A']
    s.get("mean")
    s.channels.append('FSC-B')
    s.get("mean")
    assert len(responses.calls) == 2
    s.cache_clear()


@pytest.mark.vcr()
def test_quantile_should_require_q():
    s = StatisticRequest("5e4fcb98bdd7ea051d703652")
    s.channels = ['FSC-A']
    # fails without q set
    with pytest.raises(RequestException):
        s.get("quantile")

    # passes with q set
    s.q = 0.5
    stats = s.get("quantile")
    statistics_tester(stats)
    s.cache_clear()


@pytest.mark.vcr()
def test_should_get_every_statistics_type():
    methods = ["mean", "median", "mad", "geometric_mean", "event_count", "cv", "stddev", "percent"]
    s = StatisticRequest("5e4fcb98bdd7ea051d703652")
    s.channels = ['FSC-A']
    for method in methods:
        stats = s.get(method)
        statistics_tester(stats)
        assert [snake_to_camel(method) in stat.keys() for stat in stats]
    s.cache_clear()


@pytest.mark.vcr()
def test_should_get_formatted_csv():
    s = StatisticRequest("5e4fcb98bdd7ea051d703652")
    s.format = "csv"
    s.layout = "short-wide"
    stats = s.get('mean')
    # look for rows
    assert type(stats.find('\r')) == int
    s.cache_clear()


@responses.activate
def test_should_return_pandas_dataframe(statistic_response):
    responses.add(
        responses.POST, base_url + "experiments/5e4fcb98bdd7ea051d703653/bulkstatistics", json=statistic_response
    )
    s = StatisticRequest("5e4fcb98bdd7ea051d703653")
    s.get("mean")
    stats = s.to_pandas()
    properties = [
        'fcsFileId',
        'filename',
        'populationId',
        'population',
        'uniquePopulationName',
        'parentPopulation',
        'parentPopulationId',
    ]
    assert all(prop in stats.columns.to_list() for prop in properties)
    s.cache_clear()
