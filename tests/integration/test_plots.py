import pytest
from typing import Iterator, Tuple
import os

from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.plot import Plot


@pytest.fixture()
def ligands_experiment(
    blank_experiment: Experiment,
) -> Iterator[Tuple[Experiment, FcsFile]]:
    file1 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
    )

    yield blank_experiment, file1


# Begin tests


def test_plot_get(ligands_experiment: Tuple[Experiment, FcsFile]):
    experiment, fcs_file = ligands_experiment
    plot = Plot.get(
        experiment._id,
        fcs_file._id,
        "dot",
        fcs_file.channels[0],
        fcs_file.channels[1],
    )
    assert plot.experiment_id == experiment._id
    assert plot.fcs_file_id == fcs_file._id
    assert plot.x_channel == fcs_file.channels[0]
    assert plot.y_channel == fcs_file.channels[1]
    assert plot.plot_type == "dot"
    assert plot.population_id == None
    assert hasattr(plot, "data")
    assert type(plot.data) == bytes


@pytest.mark.parametrize("plot_type", ["contour", "dot", "density", "histogram"])
def test_plot_get_each_plot_type(
    ligands_experiment: Tuple[Experiment, FcsFile], plot_type
):
    experiment, fcs_file = ligands_experiment
    Plot.get(
        experiment._id,
        fcs_file._id,
        plot_type,
        fcs_file.channels[0],
        fcs_file.channels[1],
    )


def test_plot_save(ligands_experiment: Tuple[Experiment, FcsFile]):
    experiment, fcs_file = ligands_experiment
    plot = Plot.get(
        experiment._id,
        fcs_file._id,
        "dot",
        fcs_file.channels[0],
        fcs_file.channels[1],
    )
    plot.save("test_file.png")
    with open("test_file.png", "rb") as f:
        assert f.read() == plot.data
    os.remove("test_file.png")
