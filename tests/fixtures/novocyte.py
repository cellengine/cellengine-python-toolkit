import pytest

from cellengine.resources.fcs_file import FcsFile
from cellengine.utils.fcs_file_io import FcsFileIO


@pytest.fixture(scope="session")
def novocyte():
    json = {
        "_id": "61a78df91f7ce603642c03fd",
        "gatesLocked": False,
        "deleted": None,
        "filename": "Acea - Novocyte.fcs",
        "experimentId": "61a78ddf1f7ce603642c03f9",
        "annotations": [
            {"name": "plate well", "value": "Group 1 37 pos"},
            {"name": "plate row", "value": "A"},
            {"name": "plate column", "value": "02"},
        ],
        "panel": [
            {"channel": "FSC-H", "reagent": None, "index": 1},
            {"channel": "SSC-H", "reagent": None, "index": 2},
            {"channel": "BL1-H", "reagent": "CD57-FITC-H", "index": 3},
            {"channel": "BL2-H", "reagent": "Multimer-PE-H", "index": 4},
            {"channel": "BL4-H", "reagent": "CD45RA-PerCy5-H", "index": 5},
            {"channel": "BL5-H", "reagent": "CD28-PE-Cy7-H", "index": 6},
            {"channel": "RL1-H", "reagent": "CD8-APC-H", "index": 7},
            {"channel": "RL2-H", "reagent": "CD3-APCAx750-H", "index": 8},
            {"channel": "VL1-H", "reagent": "CCR7-BV421-H", "index": 9},
            {"channel": "VL2-H", "reagent": "Aqua-H", "index": 10},
            {"channel": "VL3-H", "reagent": "Pacific Orange-H", "index": 11},
            {"channel": "FSC-A", "reagent": None, "index": 12},
            {"channel": "SSC-A", "reagent": None, "index": 13},
            {"channel": "BL1-A", "reagent": "CD57-FITC-A", "index": 14},
            {"channel": "BL2-A", "reagent": "Multimer-PE-A", "index": 15},
            {"channel": "BL4-A", "reagent": "CD45RA-PerCy5-A", "index": 16},
            {"channel": "BL5-A", "reagent": "CD28-PE-Cy7-A", "index": 17},
            {"channel": "RL1-A", "reagent": "CD8-APC-A", "index": 18},
            {"channel": "RL2-A", "reagent": "CD3-APCAx750-A", "index": 19},
            {"channel": "VL1-A", "reagent": "CCR7-BV421-A", "index": 20},
            {"channel": "VL2-A", "reagent": "Aqua-A", "index": 21},
            {"channel": "VL3-A", "reagent": "Pacific Orange-A", "index": 22},
            {"channel": "Width", "reagent": None, "index": 23},
            {"channel": "TIME", "reagent": None, "index": 24},
        ],
        "crc32c": "7d4a285e",
        "md5": "6476f790b2562d53ad674b9213f7e849",
        "size": 20360897,
        "hasFileInternalComp": True,
        "eventCount": 211974,
        "isControl": False,
        "panelName": "Panel 1",
        "__v": 0,
    }

    file = FcsFile.from_dict(json)
    with open("tests/data/Acea - Novocyte.fcs", "rb") as events:
        file.events = FcsFileIO.parse(events)
    return file
