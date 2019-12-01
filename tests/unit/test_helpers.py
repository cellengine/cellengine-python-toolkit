import os
import responses
import cellengine
from cellengine import _helpers
from cellengine.Gates.gate_util import get_fcsfile


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


@responses.activate
def test_get_fcsfile(fcsfiles):
    responses.add(
        responses.GET,
        base_url + "experiments/5d38a6f79fae87499999a74b/fcsfiles",
        json=[fcsfiles[3]],
    )
    fcsfile = get_fcsfile(
        experiment_id="5d38a6f79fae87499999a74b", name="Specimen_001_A1_A01.fcs"
    )
    assert fcsfile._id == "5d64abe2ca9df61349ed8e7c"
