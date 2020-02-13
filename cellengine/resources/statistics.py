from io import StringIO
from cachetools import cachedmethod, LRUCache
from cachetools.keys import hashkey
import attr
import pandas
from typing import List, Set, Dict, Tuple, Optional, Union
from cellengine.utils import helpers
from cellengine.utils.helpers import GetSet, base_post, snake_to_camel


def to_tuple(lst):
    return tuple(to_tuple(i) if isinstance(i, list) else i for i in lst)

def custom_key(*args, env={}):
    items = list(args[1].values())
    key = hashkey(to_tuple(items))
    return key

@attr.s
class StatisticRequest:
    """
    Helper class for requesting Statistics from CellEngine.

    Required Args:
        experiment_id: ID of experiment to request statistics for.
        statistics: Statistical method to request. Any of "mean", "median", "quantile",
            "mad" (median absolute deviation), "geometric_mean", "eventcount",
            "cv", "stddev" or "percent" (case-insensitive).
        q: int: quantile (required for "quantile" statistic)
        channels: List[str]: for "mean", "median", "geometricmean", "cv",
            "stddev", "mad" or "quantile" statistics. Names of
            channels to calculate statistics for.

    Optional Args:
        annotations: bool: Include file annotations in output (defaults to False).
        compensation_id: str: Compensation to use for gating and statistic calculation.
            Defaults to uncompensated. Three special constants may be used:
                0: Uncompensated
                -1: File-Internal Compensation Uses the file's internal compensation
                    matrix, if available. If not available, an error will be returned.
                -2: Per-File Compensation Use the compensation assigned to each
                    individual FCS file.
        fcs_file_ids: str or List[str]: FCS files to get statistics for. If omitted,
            statistics for all non-control FCS files will be returned.
        format: str: One of "TSV (with[out] header)", "CSV (with[out] header)" or
            "json" (default), case-insensitive.
        layout: str: The file (TSV/CSV) or object (JSON) layout. One of "tall-skinny",
            "medium", or "short-wide".
        percent_of: str or List[str]: Population ID or array of population IDs.
            If omitted or the string "PARENT", will calculate percent of parent for
            each population. If a single ID, will calculate percent of that population
            for all populations specified by populationIds. If a list, will calculate
            percent of each of those populations.
        population_ids: List[str]: List of population IDs. Defaults to ungated.

    Returns:
        statistics: Dict, String, or pandas.Dataframe (if
    """
    experiment_id = attr.ib()
    statistics = attr.ib(default=None)
    q = attr.ib(default=None)
    channels = attr.ib(default=[])
    annotations = attr.ib(default=False)
    compensation_id = attr.ib(default=None)
    fcs_file_ids = attr.ib(default=None)
    format = attr.ib(default="json")
    layout = attr.ib(default=None)
    percent_of = attr.ib(default=None)
    population_ids = attr.ib(default=None)
    _data = attr.ib(default=None, repr=False)
    _cache = attr.ib(default=LRUCache(maxsize=64), repr=False)

    def get(self, method: List[str] = None):
        if method:
            return self.make_request(method)
        else:
            try:
                return self.make_request(self.statistics)
            except:
                raise ValueError("You must specify a method (or methods).")

    def make_request(self, method):
        if type(method) is list:
            self.statistics = [snake_to_camel(item) for item in method]
        else:
            self.statistics = snake_to_camel(method)
        data=self._assemble_parameters()
        return self._request(method, data)

    def _assemble_parameters(self):
        params = {
            "statistics": self.statistics,
            "q": self.q,
            "channels": self.channels,
            "annotations": self.annotations,
            "compensationId": self.compensation_id,
            "fcsFileIds": self.fcs_file_ids,
            "format": self.format,
            "layout": self.layout,
            "percentOf": self.percent_of,
            "populationIds": self.population_ids,
        }
        return {key: val for key, val in params.items() if val is not None}


    @cachedmethod(lambda self: self._cache, key=custom_key)
    def _request(self, method, data):
        res = base_post("experiments/{}/bulkstatistics".format(self.experiment_id), data=data)
        if self.format == "json":
            self._data = res.json()
        else:
            try:
                self._data = res.content.decode()
            except:
                raise ValueError("Invalid output format {}".format(self.format))
        return self._data

    def to_pandas(self):
        try:
            return pandas.DataFrame.from_dict(self._data)
        except:
            raise ValueError("Invalid saved data format {} for pandas".format(self.format))

    def cache_clear(self):
        self._cache.clear()
