from cellengine.resources.fcs_file import FcsFile
import json
from cellengine.utils.parse_fcs_file import parse_fcs_file
from cellengine.resources.compensation import Compensation
import pytest
from pandas import read_json, DataFrame


@pytest.fixture(scope="function")
def acea_events() -> DataFrame:
    """Real events from 'Acea - Novocyte.fcs'"""
    events_body = open("tests/data/Acea - Novocyte.fcs", "rb")
    file = parse_fcs_file(events_body.read())
    return file.astype("float32")


@pytest.fixture(scope="function")
def acea_fcs_file(acea_events):
    with open("tests/data/acea.json", "r") as f:
        fcs_file = json.load(f)
    file = FcsFile.from_dict(fcs_file)
    file.events = acea_events
    return file


@pytest.fixture(scope="function")
def acea_compensation(acea_fcs_file):
    return Compensation.from_spill_string(acea_fcs_file.spill_string)


@pytest.fixture(scope="function")
def acea_events_compensated():
    """File-internal compensated events from 'Acea - Novocyte.fcs'"""
    file = read_json("tests/data/acea_compensated.json")
    return file.astype("float32")
