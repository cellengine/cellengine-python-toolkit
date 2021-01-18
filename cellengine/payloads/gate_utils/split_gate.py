from typing import List

import cellengine as ce
from cellengine.utils.generate_id import generate_id
from cellengine.payloads.gate_utils import format_common_gate


def format_split_gate(
    experiment_id: str,
    x_channel: str,
    name: str,
    x: str,
    y: float = 0.5,
    labels: List[str] = [],
    gid: str = None,
    gids: List[str] = None,
    locked: bool = False,
    parent_population_id: str = None,
    parent_population: str = None,
    tailored_per_file: bool = False,
    fcs_file_id: str = None,
    fcs_file: str = None,
    create_population: bool = True,
):
    """
    Formats a split gate for posting to the CE API.

    Split gates have two sectors (right and left),
    each with a unique gid and name.

    Args:
        x_channel (str): The name of the x channel to which the gate applies.
        name (str): The name of the gate.
        x (float): The x coordinate of the center point (after the channel's scale has
            been applied).
        y (float): The relative position from 0 to 1 of the dashed line extending
            from the center point.
        labels (list): Positions of the quadrant labels. A list of two length-2 lists in
            the order: L, R. These are set automatically to the top corners.
        gid (str): Group ID of the gate, used for tailoring. If this is not
            specified, then a new Group ID will be created. To create a
            tailored gate, the gid of the global tailored gate must be specified.
        gids (list): Group IDs of each sector, assigned to model.gids.
        locked (bool): Prevents modification of the gate via the web interface.
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

    Returns:
        A SplitGate object.

    Example:
        ```python
        cellengine.Gate.create_split_gate(experiment_id, x_channel="FSC-A",
        name="my gate", x=144000, y=100000)
        experiment.create_split_gate(x_channel="FSC-A", name="my gate", x=144000,
            y=100000)
        ```
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
