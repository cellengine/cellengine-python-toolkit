from __future__ import annotations
from cellengine.utils.dataclass_mixin import DataClassMixin
from dataclasses import dataclass
from typing import Optional

import cellengine as ce
from cellengine.utils.wrapped_image_opener import WrappedImageOpener


@dataclass
class Plot(DataClassMixin):
    """A class representing a CellEngine plot."""

    experiment_id: str
    fcs_file_id: str
    x_channel: str
    y_channel: str
    z_channel: Optional[str]
    plot_type: str
    population_id: Optional[str]
    data: bytes

    def __post_init__(self):
        self.image = None

    def __repr__(self):
        return f"Plot(experiment_id='{self.experiment_id}', fcs_file_id='{self.fcs_file_id}', plot_type='{self.plot_type}', x_channel='{self.x_channel}', y_channel='{self.y_channel}', z_channel='{self.z_channel}', population_id='{self.population_id}') "  # noqa

    @classmethod
    def get(
        cls,
        experiment_id: str,
        fcs_file_id: str,
        plot_type: str,
        x_channel: str,
        y_channel: str,
        z_channel: Optional[str] = None,
        population_id: Optional[str] = None,
        **kwargs,
    ) -> Plot:
        """
        Args:
            experiment_id: ID of the experiment to which the file belongs.
            fcs_file_id: ID of file for which to build a plot.
            plot_type: "contour", "dot", "density" or
                "histogram" (case-insensitive)
            x_channel: X channel name.
            y_channel: (for 2D plots) Y channel name.
            z_channel: (for dot plots colored by a 3rd channel)
                Color channel name.
            population_id: Defaults to ungated.
            **kwargs (Dict):
                - axesQ (bool): Display axes lines. Defaults to true.
                - axisLabelsQ (bool): Display axis labels. Defaults to true.
                - compensation (ID): Compensation to use for gating and display.
                - color (str): Case-insensitive string in the format
                    #rgb, #rgba, #rrggbb or #rrggbbaa. The foreground color, i.e.
                    color of curve in "histogram" plots and dots in "dot" plots.
                - gateLabel (str): One of "eventcount", "mean", "median",
                    "percent", "mad", "cv", "stddev", "geometricmean",
                    "name", "none".
                - gateLabelFontSize (float): Font size for gate labels.
                - height (int): Image height. Defaults to 228.
                - percentileStart (float): For contour plots, the percentile of the
                    first contour.
                - percentileStep (float): For contour plots, the percentile
                    step between each contour.
                - postSubsampleN (int): Randomly subsample the file to contain
                    this many events after gating.
                - postSubsampleP (float): Randomly subsample the file to contain this
                    percent of events (0 to 1) after gating.
                - preSubsampleN (int): Randomly subsample the file to contain this
                    many events before gating.
                - preSubsampleP (float): Randomly subsample the file to contain this
                    percent of events (0 to 1) before gating.
                - renderGates (bool): Render gates into the image.
                - seed (int): Seed for random number generator used for
                    subsampling. Use for deterministic (reproducible) subsampling.
                    If omitted, a pseudo-random value is used.
                - smoothing (float): For density and contour plots, adjusts the
                - strokeThickness (float): The thickness of histogram and contour
                    plot lines. Defaults to 1.
                - tickLabelsQ (bool): Display tick labels. Defaults to false.
                - ticksQ (bool): Display ticks. Defaults to true.
                - width (int): Image width. Defaults to 228.
                - xAxisLabelQ (bool): Display x axis label. Overrides axisLabelsQ.
                - xAxisQ (bool): Display x axis line. Overrides axesQ.
                - xTickLabelsQ (bool): Display x tick labels. overrides tickLabelsQ.
                - xTicksQ (bool): Display x ticks. Overrides ticksQ.
                - yAxisLabelQ (bool): Display y axis label. Overrides axisLabelsQ.
                    amount of smoothing. Defaults to 0 (no smoothing). Set to 1 for
                    typical smoothing. Higher values (up to 10) increase smoothing.
                - yAxisQ (bool): Display y axis line. Overrides axesQ.
                - yTickLabelsQ (bool): Display y tick labels. Overrides tickLabelsQ.
                - yTicksQ (bool): Display y ticks. Overrides ticksQ.
        """
        properties = None
        if kwargs:
            properties = dict(kwargs)
        return ce.APIClient().get_plot(
            experiment_id,
            fcs_file_id,
            plot_type,
            x_channel,
            y_channel,
            z_channel,
            population_id,
            properties,
        )

    def display(self):
        if not self.image:
            self.image = WrappedImageOpener().open(self.data)
        return self.image

    def save(self, filepath: str):
        with open(filepath, "wb") as f:
            f.write(self.data)
