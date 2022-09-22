import pytest
import responses
from cellengine.utils.parse_fcs_file_args import parse_fcs_file_args
from typing import List


EXP_ID = "5d38a6f79fae87499999a74b"


def test_fcs_file_and_fcs_file_id_defined():
    with pytest.raises(
        ValueError, match="Please specify only 'fcs_file' or 'fcs_file_id'."
    ):
        parse_fcs_file_args(
            experiment_id="5d38a6f79fae87499999a74b",
            tailored_per_file=True,
            fcs_file="Specimen_001_A1_A01.fcs",
            fcs_file_id="5d38a7159fae87499999a74e",
        )


def test_neither_fcs_file_nor_fcs_file_id_defined():
    assert (
        parse_fcs_file_args(
            experiment_id="5d38a6f79fae87499999a74b", tailored_per_file=True
        )
        == None
    )


def test_tailored_per_file_false():
    assert (
        parse_fcs_file_args(
            experiment_id="5d38a6f79fae87499999a74b", tailored_per_file=False
        )
        == None
    )


def test_fcs_file_id_defined():
    assert (
        parse_fcs_file_args(
            experiment_id="5d38a6f79fae87499999a74b",
            tailored_per_file=True,
            fcs_file_id="5d38a7159fae87499999a74e",
        )
        == "5d38a7159fae87499999a74e"
    )


@responses.activate
def test_fcs_file_defined(ENDPOINT_BASE, fcs_files: List[dict]):
    f3 = fcs_files[3]
    responses.add(
        responses.GET,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/fcsfiles",
        json=[f3],
    )
    responses.add(
        responses.GET,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/fcsfiles/{f3['_id']}",
        json=f3,
    )
    assert (
        parse_fcs_file_args(
            experiment_id=EXP_ID,
            tailored_per_file=True,
            fcs_file=f3["filename"],
        )
        == f3["_id"]
    )
