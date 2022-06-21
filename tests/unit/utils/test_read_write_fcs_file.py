import os
from shutil import rmtree

from flowio.flowdata import FlowData
from pandas.core.frame import DataFrame
from pandas.testing import assert_frame_equal
import pytest

from cellengine.utils import FcsFileIO
from cellengine.utils.fcs_file_io import FcsFileIOError


@pytest.fixture(scope="function")
def file_bytes():
    """Yield a test file as raw bytes

    Scopes to "function" since bytes will be read by multiple calls."""
    with open("tests/data/Acea - Novocyte.fcs", "rb") as raw:
        yield raw


class TestFcsFileIO:
    @classmethod
    def setup(cls):
        pathname = f"{cls.__name__}-files/"
        if os.path.isdir(pathname):
            rmtree(pathname)
        cls.test_dir = f"{cls.__name__}-files/"
        os.mkdir(cls.test_dir)

    @classmethod
    def teardown(cls):
        rmtree(cls.test_dir)

    def test_reads_fcs_from_binary(self, file_bytes):
        file = FcsFileIO.parse(file_bytes)
        assert isinstance(file, DataFrame)
        assert (211974, 24) == file.shape

        assert list(file.columns) == [
            "FSC-H",
            "SSC-H",
            "BL1-H",
            "BL2-H",
            "BL4-H",
            "BL5-H",
            "RL1-H",
            "RL2-H",
            "VL1-H",
            "VL2-H",
            "VL3-H",
            "FSC-A",
            "SSC-A",
            "BL1-A",
            "BL2-A",
            "BL4-A",
            "BL5-A",
            "RL1-A",
            "RL2-A",
            "VL1-A",
            "VL2-A",
            "VL3-A",
            "Width",
            "TIME",
        ]

    def test_reads_fcs_from_file_path(self):
        fileio = FcsFileIO.read("tests/data/Acea - Novocyte.fcs")
        assert isinstance(fileio, FcsFileIO)
        assert isinstance(fileio.flow_data, FlowData)

    def test_saves_fcs_flow_data(self):
        fileio = FcsFileIO.read("tests/data/Acea - Novocyte.fcs")
        filename = f"{self.test_dir}/test_save_fcs_file_io.fcs"
        fileio.save(filename)
        assert os.path.isfile(filename)

    def test_parses_fcs_from_file_path(self):
        file = FcsFileIO.parse("tests/data/Acea - Novocyte.fcs")
        assert isinstance(file, DataFrame)
        assert (211974, 24) == file.shape

    def test_writes_file_as_binary_to_destination(self, file_bytes):
        filename = f"{self.test_dir}test_write.fcs"
        FcsFileIO.write(destination=filename, file=file_bytes)

        file = FcsFileIO.parse(filename)
        assert isinstance(file, DataFrame)
        assert (211974, 24) == file.shape

    def test_writes_file_as_dataframe_to_destination(self, file_bytes):
        path = f"{self.test_dir}test_writes_fcs_file.fcs"
        file = FcsFileIO.parse(file_bytes)
        FcsFileIO.write(destination=path, file=file, channels=list(file.columns))

        assert os.path.isfile(path)
        data = FcsFileIO.parse(path)
        assert isinstance(data, DataFrame)
        assert (211974, 24) == data.shape

    def test_write_saves_channel_reagents(self, file_bytes):
        # Given: event data in a DataFrame
        path = f"{self.test_dir}test_write_fcs_file_reagents.fcs"
        file, reagents = FcsFileIO.parse(file_bytes, return_reagents=True)
        channels = list(file.columns)
        FcsFileIO.write(
            destination=path,
            file=file,
            channels=channels,
            reagents=[v for _, v in reagents.items()],
        )

        assert os.path.isfile(path)
        saved_data, saved_reagents = FcsFileIO.parse(path, return_reagents=True)
        assert saved_reagents == reagents
        assert_frame_equal(saved_data, file)

    def test_raises_for_invalid_file_input(self):
        with pytest.raises(FcsFileIOError, match="FCS file could not be read"):
            FcsFileIO.parse(b"foo")  # type: ignore
