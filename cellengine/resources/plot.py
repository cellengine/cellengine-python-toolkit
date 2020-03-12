import attr
from typing import Dict
from PIL import Image
from io import BytesIO

from cellengine.utils.helpers import GetSet, base_get, convert_dict
from cellengine.utils import helpers


@attr.s
class Plot:
    """A class representing a CellEngine plot.

    Attributes:
        experiment_id (str): ID of the experiment to which the file belongs.
        fcs_file_id (str): ID of file for which to build a plot.
        x_channel (str): X channel name.
        y_channel (str): (for 2D plots) Y channel name.
        plot_type (str): "dot", "density" or "histogram" (case-insensitive)
        properties (dict): Other optional attributes in dict form: {"property": value}
            compensation (ID): Compensation to use for gating and display.
            population_id (ID): Defaults to ungated.
            width (int): Image width. Defaults to 228.
            height (int): Image height. Defaults to 228.
            axes_q (bool): Display axes lines. Defaults to true.
            ticks_q (bool): Display ticks. Defaults to true.
            tick_labels_q (bool): Display tick labels. Defaults to false.
            axis_labels_q (bool): Display axis labels. Defaults to true.
            x_axis_q (bool): Display x axis line. Overrides axes_q.
            y_axis_q (bool): Display y axis line. Overrides axes_q.
            x_ticks_q (bool): Display x ticks. Overrides ticks_q.
            y_ticks_q (bool): Display y ticks. Overrides ticks_q.
            x_tick_labels_q (bool): Display x tick labels. Overrides tick_labels_q.
            y_tick_labels_q (bool): Display y tick labels. Overrides tick_labels_q.
            x_axis_label_q (bool): Display x axis label. Overrides axis_labels_q.
            y_axis_label_q (bool): Display y axis label. Overrides axis_labels_q.
            color (str): Case-insensitive string in the format
                #rgb, #rgba, #rrggbb or #rrggbbaa. The foreground color, i.e. color
                of curve in "histogram" plots and dots in "dot" plots.
            render_gates (bool): Render gates into the image.
            pre_subsample_n (int): Randomly subsample the file to contain this
                many events before gating.
            pre_subsample_p (float): Randomly subsample the file to contain this percent of
                events (0 to 1) before gating.
            post_subsample_n (int): Randomly subsample the file to contain
                this many events after gating.
            post_subsample_p (float): Randomly subsample the file to contain this
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
            properties = convert_dict(properties, 'snake_to_camel')
            req_params.update(properties)

        res = base_get(url, params=req_params)
        return cls(experiment_id, fcs_file, x_channel, y_channel, plot_type, res.content)

    def display(self):
        return Image.open(BytesIO(self.data))

    def save(self, filepath: str):
        with open(filepath, "wb") as f:
            f.write(self.data)
