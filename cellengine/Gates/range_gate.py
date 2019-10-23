import numpy
from custom_inherit import doc_inherit
from .. import _helpers
from .gate_util import common_gate_create, gate_style


@doc_inherit(common_gate_create, style=gate_style)
def create_range_gate(experiment_id, x_channel, name,
                      x1, x2, y=0.5, label=[], gid=None, locked=False,
                      parent_population_id=None, parent_population=None,
                      tailored_per_file=False, fcs_file_id=None,
                      fcs_file=None, create_population=True):
    """Creates a range gate.

    Args:
        y_channel: The name of the y channel to which the gate applies.
        x1: The first x coordinate (after the channel's scale has been applied).
        x2: The second x coordinate (after the channel's scale has been applied).
        y: Position of the horizontal line between the vertical lines, in the
        label: Position of the label. Defaults to the midpoint of the gate.

    Returns:
        A RangeGate object.

    Example:
        experiment.create_range_gate(x_channel="FSC-A", name="my gate",
        x1=12.502, x2=95.102)
        cellengine.Gate.create_range_gate(experiment_id,
        x_channel="FSC-A", name="my gate",
        12.502, 95.102)
        """
    if label == []:
        label = [numpy.mean([x1, x2]), y]
    if gid is None:
        gid = _helpers.generate_id()

    model = {
        'locked': locked,
        'label': label,
        'range': {'x1': x1, 'x2': x2, 'y': y}
    }

    body = {
        'experimentId': experiment_id,
        'name': name,
        'type': 'RangeGate',
        'gid': gid,
        'xChannel': x_channel,
        'parentPopulationId': parent_population_id,
        'model': model
    }

    return common_gate_create(experiment_id, body=body,
                              tailored_per_file=tailored_per_file,
                              fcs_file_id=fcs_file_id,
                              fcs_file=fcs_file, create_population=create_population)
