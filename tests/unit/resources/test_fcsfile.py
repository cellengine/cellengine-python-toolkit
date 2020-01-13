import os
import responses
from cellengine.utils.loader import Loader


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


def get_fcsfile(experiment_id=None, _id=None, name=None):
    return Loader.get_fcsfile(experiment_id=experiment_id, _id=_id, name=name)


@responses.activate
def test_get_fcsfile(fcsfiles):
    responses.add(
        responses.GET,
        base_url
        + "experiments/5d38a6f79fae87499999a74b/fcsfiles/5d64abe2ca9df61349ed8e7c",
        json=fcsfiles[3],
    )
    fcsfile = get_fcsfile(
        experiment_id="5d38a6f79fae87499999a74b", _id="5d64abe2ca9df61349ed8e7c"
    )
    assert fcsfile._id == "5d64abe2ca9df61349ed8e7c"


@responses.activate
def test_get_fcsfile_by_name(fcsfiles):
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/fcsfiles",
        json=fcsfiles[3],
    )
    responses.add(
        responses.GET,
        base_url
        + "experiments/5d38a6f79fae87499999a74b/fcsfiles/5d64abe2ca9df61349ed8e7c",
        json=fcsfiles[3],
    )
    fcsfile = get_fcsfile(
        experiment_id="5d38a6f79fae87499999a74b", name="Specimen_001_A1_A01.fcs"
    )
    assert fcsfile._id == "5d64abe2ca9df61349ed8e7c"


@responses.activate
def test_get_fcsfile_by_name_and_experiment_name(fcsfiles, experiments):
    responses.add(
        responses.GET, base_url + "experiments", json=experiments[0],
    )
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b",
        json=experiments[0],
    )
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/fcsfiles",
        json=fcsfiles[3],
    )
    responses.add(
        responses.GET,
        base_url
        + "experiments/5d38a6f79fae87499999a74b/fcsfiles/5d64abe2ca9df61349ed8e7c",
        json=fcsfiles[3],
    )
    fcsfile = get_fcsfile(
        experiment_id="5d38a6f79fae87499999a74b", name="Specimen_001_A1_A01.fcs"
    )
    assert fcsfile._id == "5d64abe2ca9df61349ed8e7c"
