import pytest
import numpy
import cellengine
from cellengine import helpers
from test_gates_integ import gate_tester


@pytest.mark.vcr()
def test_create_range_gate(experiment):
    """Test for correct creation of a range gate."""
    range_gate = experiment.create_range_gate('FSC-W', 'test_range_gate', 12.502, 95.102)
    gate_tester(range_gate)
    assert range_gate.model.range.x1 == 12.502
    assert range_gate.model.range.x2 == 95.102
    assert range_gate.model.range.y == 0.5
