from typing import List
from math import pi

import cellengine as ce
from cellengine.utils.generate_id import generate_id
from cellengine.payloads.gate_utils import format_common_gate


def format_quadrant_gate(
    experiment_id: str,
    x_channel: str,
    y_channel: str,
    name: str,
    x: float,
    y: float,
    labels: List[str] = [],
    skewable: bool = False,
    angles: List[float] = [0, pi / 2, pi, 3 * pi / 2],
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
    """Formats a quadrant gate for posting to the CellEngine API.

    Quadrant gates have four sectors (upper-right, upper-left, lower-left,
    lower-right), each with a unique gid and name.

    Args:
        x_channel (str): The name of the x channel to which the gate applies.
        y_channel (str): The name of the y channel to which the gate applies.
        name (str): The name of the gate
        x (float): The x coordinate of the center point (after the channel's scale has
            been applied).
        y (float): The y coordinate (after the channel's scale has been applied).
        labels (list): Positions of the quadrant labels. A list of four length-2
            vectors in the order: UR, UL, LL, LR. These are set automatically to
            the plot corners.
        skewable (bool): Whether the quadrant gate is skewable.
        angles (list): List of the four angles of the quadrant demarcations
        gid (str): Group ID of the gate, used for tailoring. If this is not
            specified, then a new Group ID will be created. To create a
            tailored gate, the gid of the global tailored gate must be specified.
        gids (list): Group IDs of each sector, assigned to ``model.gids``.
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
        A QuadrantGate object.

    Example:
        ```python
        cellengine.Gate.create_quadrant_gate(experimentId, x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x=160000, y=200000)
        experiment.create_quadrant_gate(x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x=160000, y=200000)
        ```
    """
    # set labels based on axis scale
    r = ce.APIClient().get_scaleset(experiment_id, as_dict=True)
    scale_min = min(x["scale"]["minimum"] for x in r["scales"])
    scale_max = max(x["scale"]["minimum"] for x in r["scales"])

    if labels == []:
        labels = [
            [scale_max, scale_max],  # upper right
            [scale_min, scale_max],  # upper left
            [scale_min, scale_min],  # lower left
            [scale_max, scale_min],  # lower right
        ]  # lower right

    elif len(labels) == 4 and all(len(label) == 2 for label in labels):
        pass
    else:
        raise ValueError("Labels must be a list of four length-2 lists.")

    if gid is None:
        gid = generate_id()
    if gids is None:
        gids = [
            generate_id(),
            generate_id(),
            generate_id(),
            generate_id(),
        ]

    names = [name + append for append in [" (UR)", " (UL)", " (LL)", " (LR)"]]

    model = {
        "locked": locked,
        "labels": labels,
        "gids": gids,
        "skewable": skewable,
        "quadrant": {"x": x, "y": y, "angles": angles},
    }

    body = {
        "experimentId": experiment_id,
        "names": names,
        "type": "QuadrantGate",
        "gid": gid,
        "xChannel": x_channel,
        "yChannel": y_channel,
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
