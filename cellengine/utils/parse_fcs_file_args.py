from typing import Optional, Union
import cellengine as ce


def parse_fcs_file_args(
    experiment_id: Optional[str] = None,
    tailored_per_file: Optional[bool] = False,
    fcs_file_id: Optional[str] = None,
    fcs_file: Optional[str] = None,
) -> Union[str, None]:
    """Finds the fcs file ID if 'tailored_per_file' is True and either
    'fcs_file' or 'fcs_file_id' are specified.
    """
    if tailored_per_file is False:
        return None
    if fcs_file is not None and fcs_file_id is not None:
        raise ValueError("Please specify only 'fcs_file' or 'fcs_file_id'.")
    if fcs_file is not None:
        if experiment_id is None:
            raise ValueError("'experiment_id' is required for by-name lookup.")
        _file = ce.APIClient().get_fcs_file(experiment_id=experiment_id, name=fcs_file)
        fcs_file_id = _file._id
    return fcs_file_id
