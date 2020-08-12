import cellengine as ce
from cellengine.utils.helpers import convert_dict


def format_common_gate(
    experiment_id, body, tailored_per_file, fcs_file_id, fcs_file, create_population
):
    """
    Args:
        experiment_id: The ID of the experiment to which to add the gate.
            Use when calling this as a static method; not needed when calling
            from an Experiment object
        name: The name of the gate
        x_channel: The name of the x channel to which the gate applies.
        <Gate Args>
        gid: Group ID of the gate, used for tailoring. If this is not
            specified, then a new Group ID will be created. If you wish you
            create a tailored gate, you must specify the gid of the global
            tailored gate.
        parent_population_id: ID of the parent population. Use ``None`` for
            the "ungated" population. If specified, do not specify
            ``parent_population``.
        parent_population: Name of the parent population. An attempt will
            be made to find the population by name.  If zero or more than
            one population exists with the name, an error will be thrown.
            If specified, do not specify ``parent_population_id``.
        tailored_per_file: Whether or not this gate is tailored per FCS file.
        fcs_file_id: ID of FCS file, if tailored per file. Use ``None`` for
            the global gate in a tailored gate group. If specified, do not
            specify ``fcs_file``.
        fcs_file: Name of FCS file, if tailored per file. An attempt will be made
            to find the file by name. If zero or more than one file exists with
            the name, an error will be thrown. Looking up files by name is
            slower than using the ID, as this requires additional requests
            to the server. If specified, do not specify ``fcs_file_id``.
        locked: Prevents modification of the gate via the web interface.
        create_population: Automatically create corresponding population.
    """
    body = parse_fcs_file_args(
        experiment_id, body, tailored_per_file, fcs_file_id, fcs_file
    )
    body = convert_dict(body, "snake_to_camel")
    return body


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
