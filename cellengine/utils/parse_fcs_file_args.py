import cellengine as ce


def parse_fcs_file_args(experiment_id, tailored_per_file, fcs_file_id, fcs_file) -> str:
    """Find the fcs file ID if 'tailored_per_file' and either 'fcs_file' or
    'fcs_file_id' are specified.
    """
    if fcs_file is not None and fcs_file_id is not None:
        raise ValueError("Please specify only 'fcs_file' or 'fcs_file_id'.")
    if fcs_file is not None and tailored_per_file is True:  # lookup by name
        _file = ce.APIClient().get_fcs_file(experiment_id=experiment_id, name=fcs_file)
        fcs_file_id = _file._id
    return fcs_file_id
