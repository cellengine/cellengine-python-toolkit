import numpy

from cellengine.utils import helpers
from cellengine.utils.generate_id import generate_id
from .gate_util import create_common_gate


def create_polygon_gate(
    experiment_id,
    x_channel,
    y_channel,
    name,
    x_vertices,
    y_vertices,
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
    """Creates a polygon gate.

    Args:
        y_channel: The name of the y channel to which the gate applies.
        x_vertices: List of x coordinates for the polygon's vertices.
        y_vertices List of y coordinates for the polygon's vertices.
        label: Position of the label. Defaults to the midpoint of the gate.

    Returns:
        A PolygonGate object.

    Example:
        experiment.create_polygon_gate(x_channel="FSC-A",
        y_channel="FSC-W", name="my gate", x_vertices=[1, 2, 3], y_vertices=[4,
        5, 6])
    """
    if label == []:
        label = [numpy.mean(x_vertices), numpy.mean(y_vertices)]
    if gid is None:
        gid = generate_id()

    model = {
        "locked": locked,
        "label": label,
        "polygon": {"vertices": [[a, b] for (a, b) in zip(x_vertices, y_vertices)]},
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

    return create_common_gate(
        experiment_id,
        body=body,
        tailored_per_file=tailored_per_file,
        fcs_file_id=fcs_file_id,
        fcs_file=fcs_file,
        create_population=create_population,
    )
