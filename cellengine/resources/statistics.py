import pandas
from typing import Union, List
from cellengine.utils.helpers import GetSet, base_post


def get_statistics(
    experiment_id: str,
    statistics: Union[str, List[str]],
    channels: List[str],
    q: float = None,
    annotations: bool = False,
    compensation_id: str = None,
    fcs_file_ids: List[str] = None,
    format: str = "json",
    layout: str = None,
    percent_of: Union[str, List[str]] = None,
    population_ids: List[str] = None,
):
    """
    Helper method for requesting Statistics from CellEngine.

    Required Args:
        experiment_id: ID of experiment to request statistics for.
        statistics: Statistical method to request. Any of "mean", "median", "quantile",
            "mad" (median absolute deviation), "geometricmean", "eventcount",
            "cv", "stddev" or "percent" (case-insensitive).
        q: int: quantile (required for "quantile" statistic)
        channels: str or List[str]: for "mean", "median", "geometricMean", "cv",
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
        fcs_file_ids: List[str]: FCS files to get statistics for. If omitted,
            statistics for all non-control FCS files will be returned.
        format: str: One of "TSV (with[out] header)", "CSV (with[out] header)" or
            "json" (default), "pandas", case-insensitive.
        layout: str: The file (TSV/CSV) or object (JSON) layout. One of "tall-skinny",
            "medium", or "short-wide".
        percent_of: str or List[str]: Population ID or array of population IDs.
            If omitted or the string "PARENT", will calculate percent of parent for
            each population. If a single ID, will calculate percent of that population
            for all populations specified by populationIds. If a list, will calculate
            percent of each of those populations.
        population_ids: List[str]: List of population IDs. Defaults to ungated.
    Returns:
        statistics: Dict, String, or pandas.Dataframe
    """

    def determine_format(f):
        if f == "pandas":
            return "json"
        else:
            return f

    params = {
        "statistics": statistics,
        "q": q,
        "channels": channels,
        "annotations": annotations,
        "compensationId": compensation_id,
        "fcsFileIds": fcs_file_ids,
        "format": determine_format(format),
        "layout": layout,
        "percentOf": percent_of,
        "populationIds": population_ids,
    }
    req_params = {key: val for key, val in params.items() if val is not None}

    res = base_post(
        "experiments/{}/bulkstatistics".format(experiment_id), data=req_params
    )

    format = format.lower()
    if format == "json":
        return res.json()
    elif "sv" in format:
        try:
            return res.content.decode()
        except ValueError as e:
            raise e("Invalid output format {}".format(format))
    elif format == "pandas":
        try:
            return pandas.DataFrame.from_dict(res.json())
        except:
            raise ValueError("Invalid data format {} for pandas".format(format))
