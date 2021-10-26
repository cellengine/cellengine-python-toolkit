import cellengine as ce


def format_common_gate(
    experiment_id, body, tailored_per_file, fcs_file_id, fcs_file, create_population
):
    """
    Args:
        experiment_id (str): The ID of the experiment to which to add the gate.
            Use when calling this as a static method; not needed when calling
            from an Experiment object
        name (str): The name of the gate
        x_channel (str): The name of the x channel to which the gate applies.
        gid (str): Group ID of the gate, used for tailoring. If this is not
            specified, then a new Group ID will be created. To create a
            tailored gate, the gid of the global tailored gate must be specified.
        parent_population_id (str): ID of the parent population. Use ``None`` for
            the "ungated" population. If specified, do not specify
            ``parent_population``.
        parent_population (str): Name of the parent population. An attempt will
            be made to find the population by name.  If zero or more than
            one population exists with the name, an error will be thrown.
            If specified, do not specify ``parent_population_id``.
        tailored_per_file (bool): Whether or not this gate is tailored per FCS file.
        fcs_file_id (str): ID of FCS file, if tailored per file. Use ``None`` for
            the global gate in a tailored gate group. If specified, do not
            specify ``fcs_file``.
        fcs_file (str): Name of FCS file, if tailored per file. An attempt will be made
            to find the file by name. If zero or more than one file exists with
            the name, an error will be thrown. Looking up files by name is
            slower than using the ID, as this requires additional requests
            to the server. If specified, do not specify ``fcs_file_id``.
        create_population (bool): Automatically create corresponding population.
    """
    # TODO: create_population
    return parse_fcs_file_args(
        experiment_id, body, tailored_per_file, fcs_file_id, fcs_file
    )


def parse_fcs_file_args(experiment_id, body, tailored_per_file, fcs_file_id, fcs_file):
    """Find the fcs file ID if 'tailored_per_file' and either 'fcs_file' or
    'fcs_file_id' are specified.
    """
    if fcs_file is not None and fcs_file_id is not None:
        raise ValueError("Please specify only 'fcs_file' or 'fcs_file_id'.")
    if fcs_file is not None and tailored_per_file is True:  # lookup by name
        _file = ce.APIClient().get_fcs_file(experiment_id=experiment_id, name=fcs_file)
        fcs_file_id = _file._id
    body["tailoredPerFile"] = tailored_per_file
    body["fcsFileId"] = fcs_file_id
    return body
