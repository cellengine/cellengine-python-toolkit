import attr
from typing import Dict
from cellengine.utils.wrapped_image import WrappedImage


@attr.s(frozen=True)
class _Plot:
    experiment_id = attr.ib()
    fcs_file_id = attr.ib()
    x_channel = attr.ib()
    y_channel = attr.ib()
    plot_type = attr.ib()
    population_id = attr.ib()
    data = attr.ib(repr=False)
