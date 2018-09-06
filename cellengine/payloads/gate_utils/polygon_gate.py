import numpy

from cellengine.utils.generate_id import generate_id
from cellengine.payloads.gate_utils import format_common_gate


def format_polygon_gate(
    experiment_id,
    x_channel,
    y_channel,
    name,
    vertices,
    label=[],
    gid=None,
    locked=False,
    parent_population_id=None,
    parent_population=None,
    tailored_per_file=False,
    fcs_file_id=None,
    fcs_file=None,
    create_population=True,
):
    """Formats a polygon gate for posting to the CE API.

    Args:
        y_channel: The name of the y channel to which the gate applies.
        vertices: List of coordinates, like [[x,y], [x,y], ...]
        label: Position of the label. Defaults to the midpoint of the gate.

    Returns:
        A PolygonGate object.

    Example:
        experiment.create_polygon_gate(x_channel="FSC-A",
        y_channel="FSC-W", name="my gate", vertices=[[1,4], [2,5], [3,6]])
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
