import os
import attr
import pytest
import responses
import cellengine
from cellengine.resources.plot import Plot
from cellengine.utils.helpers import snake_to_camel
from cellengine import FcsFile

base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


def plot_tester(plot):
    assert hasattr(plot, "experiment_id")
    assert hasattr(plot, "fcs_file_id")
    assert hasattr(plot, "x_channel")
    assert hasattr(plot, "y_channel")
    assert hasattr(plot, "plot_type")
    assert hasattr(plot, "data")
    assert type(plot.data) == bytes


@responses.activate
def test_should_get_plot(experiment, fcsfiles):
    fcsfile = FcsFile(fcsfiles[0])
    responses.add(
        responses.GET, base_url + "experiments/{}/plot".format(experiment._id),
    )
    plot = Plot.get(
        experiment._id, fcsfile._id, fcsfile.channels[0], fcsfile.channels[1], "dot"
    )
    plot_tester(plot)


@responses.activate
def test_should_get_plot_from_fcsfile(fcsfiles):
    fcsfile = FcsFile(fcsfiles[0])
    responses.add(
        responses.GET, base_url + "experiments/{}/plot".format(fcsfile.experiment_id),
    )
    plot = fcsfile.plot(fcsfile.channels[0], fcsfile.channels[1], "dot")
    plot_tester(plot)


@responses.activate
def test_should_get_each_plot_type(experiment, fcsfiles):
    fcsfile = FcsFile(fcsfiles[0])
    responses.add(
        responses.GET, base_url + "experiments/{}/plot".format(experiment._id),
    )
    for plot in ["dot", "density", "histogram"]:
        plot = Plot.get(
            experiment._id, fcsfile._id, fcsfile.channels[0], fcsfile.channels[1], plot
        )


@responses.activate
def test_should_get_plot_for_each_query_parameter(
    experiment, fcsfiles, compensations, populations
):
    fcsfile = FcsFile(fcsfiles[0])
    responses.add(
        responses.GET, base_url + "experiments/{}/plot".format(experiment._id),
    )
    parameters = {
        "compensation": compensations[0]["_id"],
        "population_id": populations[0]["_id"],
        "width": 400,
        "height": 400,
        "axes_q": False,
        "ticks_q": False,
        "tick_labels_q": True,
        "axis_labels_q": False,
        "x_axis_q": True,
        "y_axis_q": True,
        "x_ticks_q": True,
        "y_ticks_q": True,
        "x_tick_labels_q": True,
        "y_tick_labels_q": True,
        "x_axis_label_q": True,
        "y_axis_label_q": True,
        "color": "#ff0000",
        "render_gates": True,
        "pre_subsample_n": 4,
        "pre_subsample_p": 0.5,
        "post_subsample_n": 4,
        "post_subsample_p": 0.5,
        "seed": 9,
        "smoothing": 0.75,
    }
    i = 0
    for item in parameters.items():
        param_dict = {item[0]: item[1]}
        plot = Plot.get(
            experiment._id,
            fcsfile._id,
            fcsfile.channels[0],
            fcsfile.channels[1],
            "dot",
            properties=param_dict,
        )

        if item[1] == "#ff0000":
            item = ("color", "%23ff0000")

        assert snake_to_camel(item[0]) in responses.calls[i].request.url
        assert str(item[1]) in responses.calls[i].request.url
        plot_tester(plot)
        i += 1


@responses.activate
def test_should_save_plot(experiment, fcsfiles):
    fcsfile = FcsFile(fcsfiles[0])
    responses.add(
        responses.GET, base_url + "experiments/{}/plot".format(experiment._id),
    )
    plot = Plot.get(
        experiment._id, fcsfile._id, fcsfile.channels[1], fcsfile.channels[1], "dot"
    )
    plot.data = b"some bytes"
    plot.save("test_file.png")
    with open("test_file.png", "r") as f:
        assert f.readline() == "some bytes"
    os.remove("test_file.png")
