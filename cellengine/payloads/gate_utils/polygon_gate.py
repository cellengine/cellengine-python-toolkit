import numpy
from typing import List

from cellengine.utils.generate_id import generate_id
from cellengine.payloads.gate_utils import format_common_gate


def format_polygon_gate(
    experiment_id: str,
    x_channel: str,
    y_channel: str,
    name: str,
    vertices: List[float],
    label: List[str] = [],
    gid: str = None,
    locked: bool = False,
    parent_population_id: str = None,
    parent_population: str = None,
    tailored_per_file: bool = False,
    fcs_file_id: str = None,
    fcs_file: str = None,
    create_population: bool = True,
):
    """Formats a polygon gate for posting to the CE API.

    Args:
        x_channel (str): The name of the x channel to which the gate applies.
        y_channel (str): The name of the y channel to which the gate applies.
        vertices (list): List of coordinates, like [[x,y], [x,y], ...]
        label (str): Position of the label. Defaults to the midpoint of the gate.
        name (str): The name of the gate
        gid (str): Group ID of the gate, used for tailoring. If this is not
            specified, then a new Group ID will be created. To create a
            tailored gate, the gid of the global tailored gate must be specified.
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
        A PolygonGate object.

    Example:
        ```python
        experiment.create_polygon_gate(x_channel="FSC-A",
        y_channel="FSC-W", name="my gate", vertices=[[1,4], [2,5], [3,6]])
        ```
    """
    if label == []:
        label = [
            numpy.mean([item[0] for item in vertices]),
            numpy.mean([item[1] for item in vertices]),
        ]
    if gid is None:
        gid = generate_id()

    model = {
        "locked": locked,
        "label": label,
        "polygon": {"vertices": vertices},
    }

    body = {
        "experimentId": experiment_id,
        "name": name,
        "type": "PolygonGate",
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
