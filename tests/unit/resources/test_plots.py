import os
import responses
from cellengine.resources.plot import Plot
from cellengine import FcsFile

base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


def plot_tester(plot):
    assert hasattr(plot, "experiment_id")
    assert hasattr(plot, "fcs_file_id")
    assert hasattr(plot, "x_channel")
    assert hasattr(plot, "y_channel")
    assert hasattr(plot, "plot_type")
    assert hasattr(plot, "population_id")
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
    for plot in ["contour", "dot", "density", "histogram"]:
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
        "width": 400,
        "height": 400,
        "axesQ": False,
        "ticksQ": False,
        "tickLabelsQ": True,
        "axisLabelsQ": False,
        "xAxisQ": True,
        "yAxisQ": True,
        "xTicksQ": True,
        "yTicksQ": True,
        "xTickLabelsQ": True,
        "yTickLabelsQ": True,
        "xAxisLabelQ": True,
        "yAxisLabelQ": True,
        "color": "#ff0000",
        "renderGates": True,
        "preSubsampleN": 4,
        "preSubsampleP": 0.5,
        "postSubsampleN": 4,
        "postSubsampleP": 0.5,
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
            population_id=populations[0]["_id"],
        )

        if item[1] == "#ff0000":
            item = ("color", "%23ff0000")

        assert item[0] in responses.calls[i].request.url
        assert str(item[1]) in responses.calls[i].request.url
        plot_tester(plot)
        i += 1


@responses.activate
def test_should_save_plot(experiment, fcsfiles):
    fcsfile = FcsFile(fcsfiles[0])
    responses.add(
        responses.GET, base_url + "experiments/{}/plot".format(experiment._id),
    )
    # instantiate Plot directly instead of using .get because the attrs are frozen
    plot = Plot(
        experiment._id,
        fcsfile._id,
        fcsfile.channels[1],
        fcsfile.channels[1],
        "dot",
        population_id=None,
        data=b"some bytes",
    )
    plot.save("test_file.png")
    with open("test_file.png", "r") as f:
        assert f.readline() == "some bytes"
    os.remove("test_file.png")
