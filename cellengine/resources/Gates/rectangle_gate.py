import numpy
from cellengine.utils.generate_id import generate_id
from .gate_util import create_common_gate


def create_rectangle_gate(
    experiment_id,
    x_channel,
    y_channel,
    name,
    x1,
    x2,
    y1,
    y2,
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
    """Creates a rectangle gate.

    Args:
        y_channel: The name of the y channel to which the gate applies.
        x1: The first x coordinate (after the channel's scale has been applied).
        x2: The second x coordinate (after the channel's scale has been applied).
        y1: The first y coordinate (after the channel's scale has been applied).
        y2: The second y coordinate (after the channel's scale has been applied).
        label: Position of the label. Defaults to the midpoint of the gate.

    Returns:
        A RectangleGate object.

    Example:
        experiment.create_rectangle_gate(x_channel="FSC-A", y_channel="FSC-W",
        name="my gate", 12.502, 95.102, 1020, 32021.2)
        cellengine.Gate.create_rectangle_gate(experiment_id, x_channel="FSC-A",
        y_channel="FSC-W", name="my gate", x1=12.502, x2=95.102, y1=1020, y2=32021.2,
        gid=global_gate.gid)
        """
    if label == []:
        label = [numpy.mean([x1, x2]), numpy.mean([y1, y2])]
    if gid is None:
        gid = generate_id()

    model = {
        "locked": locked,
        "label": label,
        "rectangle": {"x1": x1, "x2": x2, "y1": y1, "y2": y2},
    }

    body = {
        "experimentId": experiment_id,
        "name": name,
        "type": "RectangleGate",
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
