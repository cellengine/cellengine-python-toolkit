from __future__ import annotations
from attr import define, field
from typing import Any, Optional

from cellengine.utils.wrapped_image_opener import WrappedImageOpener


@define(slots=False)
class Plot:
    """A class representing a CellEngine plot."""

    experiment_id: str
    fcs_file_id: str
    x_channel: str
    y_channel: str
    z_channel: str
    plot_type: str
    data: bytes
    population_id: Optional[str] = field(default=None)
    image: Optional[Any] = field(default=None)

    def __repr__(self):
        return f"Plot(experiment_id='{self.experiment_id}', fcs_file_id='{self.fcs_file_id}', plot_type='{self.plot_type}', x_channel='{self.x_channel}', y_channel='{self.y_channel}', z_channel='{self.z_channel}', population_id='{self.population_id}') "  # noqa

    def display(self):
        if not self.image:
            self.image = WrappedImageOpener().open(self.data)
        return self.image

    def save(self, filepath: str):
        with open(filepath, "wb") as f:
            f.write(self.data)
