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

    res = base_post("experiments/{}/bulkstatistics".format(experiment_id), data=req_params)

    format = format.lower()
    if format == "json":
        return res.json()
    elif ("sv" in format):
        try:
            return res.content.decode()
        except ValueError as e:
            raise e("Invalid output format {}".format(format))
    elif format == "pandas":
        try:
            return pandas.DataFrame.from_dict(res.json())
        except:
            raise ValueError("Invalid data format {} for pandas".format(format))
