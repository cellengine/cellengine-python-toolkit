from math import pi
from custom_inherit import doc_inherit
from .. import _helpers
from .gate_util import common_gate_create, gate_style


@doc_inherit(common_gate_create, style=gate_style)
def create_quadrant_gate(experiment_id, x_channel, y_channel, name,
                      x, y, labels=[], gid=None, gids=None, locked=False,
                      parent_population_id=None, parent_population=None,
                      tailored_per_file=False, fcs_file_id=None,
                      fcs_file=None, create_population=True):
    """
    Creates a quadrant gate. Quadrant gates have four sectors (upper-right,
    upper-left, lower-left, lower-right), each with a unique gid and name.

    Args:
        x: The x coordinate of the center point (after the channel's scale has
            been applied).
        y: The y coordinate (after the channel's scale has been applied).
        labels: Positions of the quadrant labels. A list of four length-2
            vectors in the order: UR, UL, LL, LR. These are set automatically to
            the plot corners.
        gids: Group IDs of each sector, assigned to ``model.gids``.

    Returns:
        A QuadrantGate object.

    Example:
        cellengine.Gate.create_quadrant_gate(experimentId, x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x=160000, y=200000)
        experiment.create_quadrant_gate(x_channel="FSC-A",
            y_channel="FSC-W", name="my gate", x=160000, y=200000)
    """

    # future args
    skewable = False
    angles = [pi/2, pi, 3/2*pi, 0.000000]

    # set labels based on axis scale
    r = _helpers.base_get(f'experiments/{experiment_id}/scalesets')[0]
    scale_min = min(x['scale']['minimum'] for x in r['scales'])
    scale_max = max(x['scale']['minimum'] for x in r['scales'])

    if labels == []:
        labels = [[scale_max, scale_max],  # upper right
                  [scale_min, scale_max],  # upper left
                  [scale_min, scale_min],  # lower left
                  [scale_max, scale_min]]  # lower right

    elif len(labels) == 4 and all(len(label) == 2 for label in labels):
        pass
    else:
        raise ValueError('Labels must be a list of four length-2 lists.')

    if gid is None:
        gid = _helpers.generate_id()
        if gids is None:
            gids = [_helpers.generate_id(), _helpers.generate_id(),
                    _helpers.generate_id(), _helpers.generate_id()]

    names = [name + append for append in [" (UR)", " (UL)", " (LL)", " (LR)"]]

    model = {
        'locked': locked,
        'labels': labels,
        'gids': gids,
        'skewable': skewable,
        'quadrant': {'x': x, 'y': y, 'angles': angles}
    }

    body = {
        'experimentId': experiment_id,
        'names': names,
        'type': 'QuadrantGate',
        'gid': gid,
        'xChannel': x_channel,
        'yChannel': y_channel,
        'parentPopulationId': parent_population_id,
        'model': model
    }

    return common_gate_create(experiment_id, body=body,
                              tailored_per_file=tailored_per_file,
                              fcs_file_id=fcs_file_id,
                              fcs_file=fcs_file, create_population=create_population)
