import os
import cellengine
from cellengine.utils import helpers


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")


def test_make_class(gates):
    gates = helpers.make_class(cellengine.Gate, gates)
    assert type(gates) is list
    assert all([type(gate) is cellengine.Gate for gate in gates])
