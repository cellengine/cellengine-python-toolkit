import pytest
import numpy
from cellengine import helpers
from test_gates_integ import gate_tester


@pytest.mark.vcr()
def test_create_ellipse_gate(experiment):
    """Test for correct creation of a ellipse gate."""
    ellipse_gate = experiment.create_ellipse_gate("FSC-A", "FSC-W", "my gate",
                                                  260000, 64000, 0, 120000, 70000)
    gate_tester(ellipse_gate)
    assert ellipse_gate.model.ellipse.center == [260000, 64000]
    assert ellipse_gate.model.ellipse.angle == 0
    assert ellipse_gate.model.ellipse.major == 120000
    assert ellipse_gate.model.ellipse.minor == 70000
