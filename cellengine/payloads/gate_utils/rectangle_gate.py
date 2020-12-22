import numpy
from cellengine.utils.generate_id import generate_id
from cellengine.payloads.gate_utils import format_common_gate


def format_rectangle_gate(
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
    """Formats a rectangle gate for posting to the CE API.

    Args:
        experiment_id (str): The ID of the experiment to which to add the gate.
            Use when calling this as a static method; not needed when calling
            from an Experiment object
        name (str): The name of the gate
        x_channel (float): The name of the x channel to which the gate applies.
        y_channel (float): The name of the y channel to which the gate applies.
        x1 (float): The first x coordinate (after the channel's scale has been applied).
        x2 (float): The second x coordinate (after the channel's scale
            has been applied).
        y1 (float): The first y coordinate (after the channel's scale has been applied).
        y2 (float): The second y coordinate (after the channel's scale has
            been applied).
        label (float): Position of the label. Defaults to the midpoint of the gate.
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

    return format_common_gate(
        experiment_id,
        body=body,
        tailored_per_file=tailored_per_file,
        fcs_file_id=fcs_file_id,
        fcs_file=fcs_file,
        create_population=create_population,
    )
