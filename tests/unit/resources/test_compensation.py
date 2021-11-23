from cellengine.utils.parse_fcs_file import parse_fcs_file
from cellengine.resources.fcs_file import FcsFile
import json
import pytest
import responses
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from numpy import identity
from cellengine.resources.compensation import Compensation


EXP_ID = "5d38a6f79fae87499999a74b"


@pytest.fixture(scope="function")
def fcs_file(ENDPOINT_BASE, client, fcs_files):
    file = fcs_files[0]
    file.update({"experimentId": EXP_ID})
    return FcsFile.from_dict(file)


@pytest.fixture(scope="function")
def compensation(ENDPOINT_BASE, client, fcs_file, compensations):
    comp = compensations[0]
    comp.update({"experimentId": EXP_ID})
    return Compensation.from_dict(comp)


def properties_tester(comp):
    assert type(comp) is Compensation
    assert hasattr(comp, "_id")
    assert hasattr(comp, "name")
    assert hasattr(comp, "experiment_id")
    assert hasattr(comp, "channels")
    assert hasattr(comp, "N")
    assert comp.N == len(comp.dataframe)
    assert hasattr(comp, "dataframe")
    assert type(comp.dataframe) is DataFrame
    assert all(comp.dataframe.index == comp.channels)
    assert hasattr(comp, "apply")
    assert hasattr(comp, "dataframe_as_html")


def test_compensation_properties(ENDPOINT_BASE, compensation):
    properties_tester(compensation)


@responses.activate
def test_should_post_compensation(ENDPOINT_BASE, experiment, compensations):
    responses.add(
        responses.POST,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/compensations",
        json=compensations[0],
    )
    payload = compensations[0].copy()
    comp = Compensation.create(experiment._id, payload)
    properties_tester(comp)


@responses.activate
def test_should_delete_compensation(ENDPOINT_BASE, compensation):
    responses.add(
        responses.DELETE,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/compensations/{compensation._id}",
    )
    deleted = compensation.delete()
    assert deleted is None


@responses.activate
def test_should_update_compensation(ENDPOINT_BASE, compensation):
    """Test that the .update() method makes the correct call. Does not test
    that the correct response is made; this should be done with an integration
    test.
    """
    # patch the mocked response with the correct values
    response = compensation.to_dict().copy()
    response.update({"name": "newname"})
    responses.add(
        responses.PATCH,
        ENDPOINT_BASE + f"/experiments/{EXP_ID}/compensations/{compensation._id}",
        json=response,
    )
    compensation.name = "newname"
    compensation.update()
    properties_tester(compensation)
    assert json.loads(responses.calls[0].request.body) == compensation.to_dict()


def test_create_from_spill_string(spillstring):
    comp = Compensation.from_spill_string(spillstring)
    spillstring.replace
    assert type(comp) is Compensation

    assert comp.channels == [
        "Ax488-A",
        "PE-A",
        "PE-TR-A",
        "PerCP-Cy55-A",
        "PE-Cy7-A",
        "Ax647-A",
        "Ax700-A",
        "Ax750-A",
        "PacBlu-A",
        "Qdot525-A",
        "PacOrange-A",
        "Qdot605-A",
        "Qdot655-A",
        "Qdot705-A",
    ]


@responses.activate
def test_apply_comp_errors_for_nonmatching_channels(
    client, ENDPOINT_BASE, compensation, fcs_file
):
    events_body = open("tests/data/Acea - Novocyte.fcs", "rb")
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{fcs_file._id}.fcs",
        body=events_body,
    )
    events = parse_fcs_file(client.download_fcs_file(EXP_ID, fcs_file._id))
    fcs_file.events = events

    with pytest.raises(IndexError):
        compensation.apply(fcs_file)


@responses.activate
def test_apply_compensation_to_fcs_file_with_matching_kwargs(
    client, ENDPOINT_BASE, compensation, fcs_file
):
    # Given: a Compensation with channels as a subset of the FcsFile events
    responses.add(
        responses.GET,
        f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{fcs_file._id}.fcs",
        body=open("tests/data/Acea - Novocyte.fcs", "rb"),
    )
    events = fcs_file.get_events(inplace=True, testKwarg="foo")
    assert fcs_file._events_kwargs == {"testKwarg": "foo"}

    ix = list(events.columns)
    compensation.dataframe = DataFrame(identity(24), index=ix, columns=ix)
    compensation.channels = ix

    # When: a Compensation is applied
    results = compensation.apply(fcs_file, testKwarg="foo")

    # Then: events should be compensated
    assert all(results == events)
    assert (
        responses.assert_call_count(
            f"{ENDPOINT_BASE}/experiments/{EXP_ID}/fcsfiles/{fcs_file._id}.fcs?testKwarg=foo",
            1,
        )
        is True
    )


@responses.activate
def test_apply_comp_compensates_values(
    acea_events_compensated, acea_fcs_file, acea_compensation
):
    """This test compares results from a file-internal compensation conducted
    by the Python toolkit to one conducted by CellEngine. See
    tests/fixtures/compensated_events.py for details on the fixtures used
    here."""
    # Given:
    # - a file-internal compensation (see tests/fixtures/compensated_events.py)
    # - an FcsFile with uncompensated events

    # When: the Compensation is applied to a file
    results = acea_compensation.apply(acea_fcs_file, inplace=False)

    # Then: events should be compensated correctly
    assert_frame_equal(results.head(5), acea_events_compensated.head(5))
