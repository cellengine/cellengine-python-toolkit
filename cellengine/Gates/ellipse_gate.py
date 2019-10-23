from .gate_util import create_common_gate
from .. import helpers


def create_ellipse_gate(
    experiment_id,
    x_channel,
    y_channel,
    name,
    x,
    y,
    angle,
    major,
    minor,
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
    """Creates an ellipse gate.

    Args:
        y_channel: The name of the y channel to which the gate applies.
        x: The x centerpoint of the gate.
        y: The y centerpoint of the gate.
        angle: The angle of the ellipse in radians.
        major: The major radius of the ellipse.
        minor: The minor radius of the ellipse.
        label: Position of the label. Defaults to the midpoint of the gate.

    Returns:
        An EllipseGate object.

    Example:
        cellengine.Gate.create_ellipse_gate(experiment_id, x_channel="FSC-A",
        y_channel="FSC-W", name="my gate", x=260000, y=64000, angle=0,
        major=120000, minor=70000)
    """
    if label == []:
        label = [x, y]
    if gid is None:
        gid = helpers.generate_id()

    model = {
        "locked": locked,
        "label": label,
        "ellipse": {"angle": angle, "major": major, "minor": minor, "center": [x, y]},
    }

    body = {
        "experimentId": experiment_id,
        "name": name,
        "type": "EllipseGate",
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
