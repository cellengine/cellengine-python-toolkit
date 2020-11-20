import responses
import pytest
from unittest import mock
from pandas import DataFrame
from math import isclose

from cellengine.resources.scaleset import ScaleSet
from cellengine.resources.fcs_file import FcsFile


EXP_ID = "5d38a6f79fae87499999a74b"
SCALESET_ID = "5d38a6f79fae87499999a74c"


@responses.activate
def test_should_get_scaleset(ENDPOINT_BASE, client, scalesets):
    responses.add(
        responses.GET,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/scalesets",
        json=[scalesets],
    )
    ScaleSet.get(EXP_ID)


@responses.activate
def test_should_update_scaleset(ENDPOINT_BASE, client, scalesets):
    responses.add(
        responses.PATCH,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/scalesets/{SCALESET_ID}",
        json=scalesets,
    )
    s = ScaleSet(scalesets)
    s.name = "new scaleset"
    s.update()


def test_should_contain_scale_entities(scalesets):
    s = ScaleSet(scalesets)
    assert s.scales["FSC-A"]["type"] == "LinearScale"


def test_should_update_scale_value(scalesets):
    scaleset = ScaleSet(scalesets)
    assert scaleset.scales["Time"]["minimum"] == 1
    scaleset.scales["Time"]["minimum"] = 5
    assert scaleset.scales["Time"]["minimum"] == 5


def test_should_update_internal_properties_when_update_is_called(
    ENDPOINT_BASE, client, scalesets
):
    scaleset = ScaleSet(scalesets)
    scaleset.scales["Time"]["minimum"] = 5
    assert scaleset.scales["Time"]["minimum"] == 5

    scaleset._save_scales()
    assert scaleset._properties["scales"]
    assert scaleset._properties["scales"][-1]["scale"]["minimum"] == 5


@mock.patch(
    "cellengine.resources.fcs_file.FcsFile.events", new_callable=mock.PropertyMock
)
def test_raise_when_scale_type_does_not_exist(fcs_events_mock, fcs_files):
    # Given:
    fcs_events_mock.return_value = DataFrame(
        {"Time": [10, 7, 1.2, 9, 40], "Light": [0, 1, 9.4, 100, 1]}
    )
    file = FcsFile(fcs_files[0])

    # When: scale is of nonexistent type
    scaleset = ScaleSet(
        {
            "_id": SCALESET_ID,
            "experimentId": EXP_ID,
            "name": "test",
            "scales": [
                {
                    "channelName": "Time",
                    "scale": {"type": "NotAScale", "minimum": 1, "maximum": 1},
                },
            ],
        }
    )
    # Then:
    with pytest.raises(ValueError, match="'NotAScale' is not a valid scale type."):
        scaleset.apply(file, clamp_q=True)


@mock.patch(
    "cellengine.resources.fcs_file.FcsFile.events", new_callable=mock.PropertyMock
)
def test_should_apply_simple_scale_from_scaleset(
    fcs_events_mock, ENDPOINT_BASE, client, fcs_files
):
    # Given:
    fcs_events_mock.return_value = DataFrame(
        {"Time": [10, 7, 1.2, 9, 40], "Light": [0, 1, 9.4, 100, 1]}
    )
    file = FcsFile(fcs_files[0])

    # When:
    scaleset = ScaleSet(
        {
            "_id": SCALESET_ID,
            "experimentId": EXP_ID,
            "name": "test",
            "scales": [
                {
                    "channelName": "Time",
                    "scale": {"maximum": 10, "minimum": 5, "type": "LinearScale"},
                },
                {
                    "channelName": "Light",
                    "scale": {"maximum": 100, "minimum": 5, "type": "LinearScale"},
                },
            ],
        }
    )

    data = file.events
    assert all(data["Time"] == [10, 7, 1.2, 9, 40])
    assert all(data["Light"] == [0, 1, 9.4, 100, 1])

    # Then: scales should be correctly applied
    output = scaleset.apply(file, clamp_q=True, in_place=False)
    assert all(output["Time"] == [10.0, 7.0, 5.0, 9.0, 10.0])
    assert all(output["Light"] == [5.0, 5.0, 9.4, 100.0, 5.0])


@mock.patch(
    "cellengine.resources.fcs_file.FcsFile.events", new_callable=mock.PropertyMock
)
def test_should_apply_scale_when_scaleset_is_updated(
    fcs_events_mock, ENDPOINT_BASE, client, fcs_files
):
    # Given:
    fcs_events_mock.return_value = DataFrame(
        {"Time": [10, 7, 1.2, 9, 40], "Light": [0, 1, 9.4, 100, 1]}
    )
    file = FcsFile(fcs_files[0])
    scaleset = ScaleSet(
        {
            "_id": SCALESET_ID,
            "experimentId": EXP_ID,
            "name": "test",
            "scales": [
                {
                    "channelName": "Time",
                    "scale": {"maximum": 10, "minimum": 5, "type": "LinearScale"},
                },
                {
                    "channelName": "Light",
                    "scale": {"maximum": 100, "minimum": 5, "type": "LinearScale"},
                },
            ],
        }
    )

    data = file.events
    assert all(data["Time"] == [10, 7, 1.2, 9, 40])
    assert all(data["Light"] == [0, 1, 9.4, 100, 1])

    # When: scalesets are updated
    scaleset.scales["Time"]["maximum"] = 100
    # scaleset.scales["Light"].update({"minimum": 1})
    scaleset.scales["Light"] = {"maximum": 100, "minimum": 1, "type": "LinearScale"}

    # Then: scales should be correctly applied
    output = scaleset.apply(file, clamp_q=True, in_place=False)
    assert all(output["Time"] == [10, 7, 5, 9, 40])
    assert all(output["Light"] == [1, 1, 9.4, 100.0, 1])


@mock.patch(
    "cellengine.resources.fcs_file.FcsFile.events", new_callable=mock.PropertyMock
)
def test_should_apply_all_scale_types(
    fcs_events_mock, ENDPOINT_BASE, client, fcs_files
):
    # Given:
    # fmt: off
    fcs_events_mock.return_value = DataFrame(
        {
            "Time": [10, 7, 1.2, 9, 10, 11, 12, 40],
            "Light": [-250, -20, -2, -0.01, 0, 0.2, 0.5, 1],
            "Fear": [-20, 0.01, 0.5, 2, 10, 250, 1000, 10000],
        }
    )
    # fmt: on
    file = FcsFile(fcs_files[0])

    # When:
    scaleset = ScaleSet(
        {
            "_id": SCALESET_ID,
            "experimentId": EXP_ID,
            "name": "test",
            "scales": [
                {
                    "channelName": "Time",
                    "scale": {"maximum": 10, "minimum": 5, "type": "LinearScale"},
                },
                {
                    "channelName": "Light",
                    "scale": {
                        "maximum": 5000,
                        "minimum": -200,
                        "cofactor": 5,
                        "type": "ArcSinhScale",
                    },
                },
                {
                    "channelName": "Fear",
                    "scale": {"maximum": 10, "minimum": 5, "type": "LogScale"},
                },
            ],
        }
    )

    # Then: scales should be correctly applied
    data = file.events
    assert all(data["Time"] == [10, 7, 1.2, 9, 10, 11, 12, 40])
    assert all(data["Light"] == [-250, -20, -2, -0.01, 0, 0.2, 0.5, 1])
    assert all(data["Fear"] == [-20, 0.01, 0.5, 2, 10, 250, 1000, 10000])

    output = scaleset.apply(file, clamp_q=True, in_place=False)

    assert all(output["Time"] == [10, 7, 5, 9, 10, 10, 10, 10])
    assert all(
        isclose(a, b, rel_tol=0.00001)
        for a, b in zip(
            output["Light"],
            [
                -4.382182848065498,
                -2.0947125472611012,
                -0.3900353197707155,
                -0.0019999986666690665,
                0,
                0.03998934100602701,
                0.09983407889920756,
                0.19869011034924142,
            ],
        )
    )

    MINV = 0.6989700043360186
    MAXV = 1
    expected = [MINV, MINV, MINV, MINV, 1, MAXV, MAXV, MAXV]
    # fmt: off
    assert all(
        [isclose(a, b, rel_tol=0.00001) for a, b in zip(output["Fear"], expected)]
    )
    # fmt: on


@responses.activate
@mock.patch(
    "cellengine.resources.fcs_file.FcsFile.events", new_callable=mock.PropertyMock
)
def test_should_apply_scale_to_file(
    fcs_events_mock, ENDPOINT_BASE, client, scalesets, fcs_files, events
):
    # Given:
    file = FcsFile(fcs_files[0])
    responses.add(
        responses.GET, f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{file._id}.fcs",
    )

    keys = ["FSC-A", "FSC-W", "Time"]  # limit to a few keys
    trimmed_scales = [a for a in scalesets["scales"] if a["channelName"] in keys]
    scalesets.update({"scales": trimmed_scales})
    scaleset = ScaleSet(scalesets)

    # patch FcsFile().events() to directly return a dataframe
    fcs_events_mock.return_value = events[keys]

    data = file.events
    assert isclose(data["FSC-A"].iloc[0], 191267.86, rel_tol=0.00001)

    # When: scalesets are updated
    scaleset.scales["FSC-A"]["minimum"] = 10
    scaleset.scales["FSC-A"]["maximum"] = 100

    # Then: scales should be correctly applied
    output = scaleset.apply(file, clamp_q=True, in_place=False)
    assert output["FSC-A"].max() <= 100
    assert output["FSC-A"].min() >= 10
