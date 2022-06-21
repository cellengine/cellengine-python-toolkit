import os
from shutil import rmtree

import fcsparser
from pandas.core.frame import DataFrame
import pytest

from cellengine.utils.parse_fcs_file import parse_fcs_file


@pytest.fixture(scope="class")
def file_bytes():
    with open("tests/data/Acea - Novocyte.fcs", "rb") as raw:
        content = raw.read()
    yield content


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
        file = parse_fcs_file(file_bytes)
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

    def test_writes_fcs_to_file(self, file_bytes):
        filename = f"{self.test_dir}test_write.fcs"
        parse_fcs_file(file_bytes, destination=filename)

        meta, data = fcsparser.parse(filename)
        assert isinstance(meta, dict)
        assert isinstance(data, DataFrame)
        assert (211974, 24) == data.shape
        assert "__header__" in meta.keys()
