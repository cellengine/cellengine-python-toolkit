import json
import pytest
import responses


EXP_ID = "5d38a6f79fae87499999a74b"


@pytest.fixture(scope="module")
def statistic_response(experiment, statistics):
    return statistics


@pytest.mark.usefixtures("block_request")
class TestStatistics:
    @responses.activate
    def test_should_get_statistics(self, client, ENDPOINT_BASE, statistics):
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
        assert set(expected_query_body) == set(
            json.loads(responses.calls[0].request.body)
        )

    @pytest.mark.vcr
    def test_should_get_list_of_stats(self, ENDPOINT_BASE, client):
        methods_to_get = ["mean", "mad", "stddev"]
        stats = client.get_statistics(
            "5e4fcb98bdd7ea051d703652", methods_to_get, "FSC-A"
        )
        assert all([method in stats[0].keys() for method in methods_to_get])

    @pytest.mark.vcr
    def test_should_get_list_of_channels(self, ENDPOINT_BASE, client):
        channels_to_get = ["FSC-A", "FSC-H"]
        stats = client.get_statistics(
            "5e4fcb98bdd7ea051d703652", "mean", channels_to_get
        )
        assert any([channels_to_get[0] in stat["channel"] for stat in stats])
        assert any([channels_to_get[1] in stat["channel"] for stat in stats])

    @pytest.mark.vcr
    def test_quantile_should_require_q(self, ENDPOINT_BASE, client):
        with pytest.raises(ValueError):
            client.get_statistics("5e4fcb98bdd7ea051d703652", "quantile", "FSC-A")

        # passes with q set
        client.get_statistics("5e4fcb98bdd7ea051d703652", "quantile", "FSC-A", q=0.75)

    @pytest.mark.vcr
    def test_should_get_every_statistics_type(self, ENDPOINT_BASE, client):
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
            stats = client.get_statistics("5e4fcb98bdd7ea051d703652", method, "FSC-A")
            assert [method in stat.keys() for stat in stats]

    @pytest.mark.vcr
    def test_should_get_formatted_csv(self, ENDPOINT_BASE, client):
        stats = client.get_statistics(
            "5e4fcb98bdd7ea051d703652",
            "mean",
            "FSC-A",
            format="csv",
            layout="short-wide",
        )
        # count rows by row delimiter:
        assert type(stats.find("\r")) == int

    @responses.activate
    def test_should_return_pandas_dataframe(
        self, ENDPOINT_BASE, client, statistic_response
    ):
        responses.add(
            responses.POST,
            f"{ENDPOINT_BASE}/experiments/5e4fcb98bdd7ea051d703653/bulkstatistics",
            json=statistic_response,
        )
        stats = client.get_statistics(
            "5e4fcb98bdd7ea051d703653", "mean", "FSC-A", format="pandas"
        )
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
