import cellengine as ce
from cellengine.utils.generate_id import generate_id
from cellengine.payloads.gate_utils import format_common_gate


def format_split_gate(
    experiment_id,
    x_channel,
    name,
    x,
    y=0.5,
    labels=[],
    gid=None,
    gids=None,
    locked=False,
    parent_population_id=None,
    parent_population=None,
    tailored_per_file=False,
    fcs_file_id=None,
    fcs_file=None,
    create_population=True,
):
    """
    Formats a split gate for posting to the CE API.

    Split gates have two sectors (right and left),
    each with a unique gid and name.

    Args:
        experiment_id: The ID of the experiment to which to add the gate.
            Use when calling this as a static method; not needed when calling
            from an Experiment object
        x_channel: The name of the x channel to which the gate applies.
        name: The name of the gate
        x: The x coordinate of the center point (after the channel's scale has
            been applied).
        y: The relative position from 0 to 1 of the dashed line extending
           from the center point.
        labels: Positions of the quadrant labels. A list of two length-2 lists in
            the order: L, R. These are set automatically to the top corners.
        gid: Group ID of the gate, used for tailoring. If this is not
            specified, then a new Group ID will be created. To create a
            tailored gate, the gid of the global tailored gate must be specified.
        gids: Group IDs of each sector, assigned to model.gids.
        locked: Prevents modification of the gate via the web interface.
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
        create_population: Automatically create corresponding population.

    Returns:
        A SplitGate object.

    Example:
        cellengine.Gate.create_split_gate(experiment_id, x_channel="FSC-A",
        name="my gate", x=144000, y=100000)
        experiment.create_split_gate(x_channel="FSC-A", name="my gate", x=144000,
            y=100000)
    """
    # set labels based on axis scale
    r = ce.APIClient().get_scaleset(experiment_id, as_dict=True)
    scale_min = min(x["scale"]["minimum"] for x in r["scales"])
    scale_max = max(x["scale"]["minimum"] for x in r["scales"])

    if labels == []:
        labels = [
            [scale_min + 0.1 * scale_max, 0.916],
            [scale_max - 0.1 * scale_max, 0.916],
        ]
    elif len(labels) == 2 and len(labels[0]) == 2 and len(labels[1]) == 2:
        pass
    else:
        raise ValueError("Labels must be a list of two length-2 lists.")

    if gid is None:
        gid = generate_id()
        if gids is None:
            gids = [generate_id(), generate_id()]

    names = [name + " (L)", name + " (R)"]

    model = {
        "locked": locked,
        "labels": labels,
        "gids": gids,
        "split": {"x": x, "y": y},
    }

    body = {
        "experimentId": experiment_id,
        "names": names,
        "type": "SplitGate",
        "gid": gid,
        "xChannel": x_channel,
        "parentPopulationId": parent_population_id,
        "model": model,
    }

    return format_common_gate(
        experiment_id,
        body=body,
        tailored_per_file=tailored_per_file,
        fcs_file_id=fcs_file_id,
        fcs_file=fcs_file,
        create_population=create_population,
    )
