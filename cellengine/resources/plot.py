import attr
from typing import Dict
from cellengine.utils.wrapped_image import WrappedImage

from cellengine.utils.helpers import GetSet, base_get, convert_dict


@attr.s
class Plot:
    """A class representing a CellEngine plot.

    Attributes:
        experiment_id (str): ID of the experiment to which the file belongs.
        fcs_file_id (str): ID of file for which to build a plot.
        x_channel (str): X channel name.
        y_channel (str): (for 2D plots) Y channel name.
        plot_type (str): "dot", "density" or "histogram" (case-insensitive)
        properties (dict): Other optional attributes in dict form (camelCase): {"property": value}
            compensation (ID): Compensation to use for gating and display.
        population_id (ID): Defaults to ungated.
            width (int): Image width. Defaults to 228.
            height (int): Image height. Defaults to 228.
            axesQ (bool): Display axes lines. Defaults to true.
            ticksQ (bool): Display ticks. Defaults to true.
            tickLabelsQ (bool): Display tick labels. Defaults to false.
            axisLabelsQ (bool): Display axis labels. Defaults to true.
            xAxisQ (bool): Display x axis line. Overrides axes_q.
            yAxisQ (bool): Display y axis line. Overrides axes_q.
            xTicksQ (bool): Display x ticks. Overrides ticks_q.
            yTicksQ (bool): Display y ticks. Overrides ticks_q.
            xTickLabelsQ (bool): Display x tick labels. Overrides tick_labels_q.
            yTickLabelsQ (bool): Display y tick labels. Overrides tick_labels_q.
            xAxisLabelQ (bool): Display x axis label. Overrides axis_labels_q.
            yAxisLabelQ (bool): Display y axis label. Overrides axis_labels_q.
            color (str): Case-insensitive string in the format
                #rgb, #rgba, #rrggbb or #rrggbbaa. The foreground color, i.e. color
                of curve in "histogram" plots and dots in "dot" plots.
            renderGates (bool): Render gates into the image.
            preSubsampleN (int): Randomly subsample the file to contain this
                many events before gating.
            preSubsampleP (float): Randomly subsample the file to contain this percent of
                events (0 to 1) before gating.
            postSubsampleN (int): Randomly subsample the file to contain
                this many events after gating.
            postSubsampleP (float): Randomly subsample the file to contain this
                percent of events (0 to 1) after gating.
            seed (float): Seed for random number generator used for
                subsampling. Use for deterministic (reproducible) subsampling. If
                omitted, a pseudo-random value is used.
            smoothing (float): For density plots, adjusts the amount of
                smoothing. Defaults to 0 (no smoothing). Set to 1 for optimal
                smoothing. Higher values increase smoothing.
    """

    experiment_id = attr.ib()
    fcs_file_id = attr.ib()
    x_channel = attr.ib()
    y_channel = attr.ib()
    plot_type = attr.ib()
    data = attr.ib(repr=False)

    @classmethod
    def get(
        cls,
        experiment_id,
        fcs_file,
        x_channel,
        y_channel,
        plot_type,
        properties: Dict = None,
    ):
        url = "experiments/{0}/plot".format(experiment_id)

        req_params = {
            "fcsFileId": fcs_file,
            "xChannel": x_channel,
            "yChannel": y_channel,
            "plotType": plot_type,
            "populationId": "null"
            #TODO: make populationId not required (bug)
        }

        if properties:
            req_params.update(properties)

        res = base_get(url, params=req_params)
        return cls(experiment_id, fcs_file, x_channel, y_channel, plot_type, res.content)

    def display(self):
        return WrappedImage().open(self.data)

    def save(self, filepath: str):
        with open(filepath, "wb") as f:
            f.write(self.data)
