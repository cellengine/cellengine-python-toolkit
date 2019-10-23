import pytest
import cellengine
from cellengine._helpers import ID_REGEX


@pytest.mark.vcr()
def test_get_experiment(client):
    """Tests getting an experiment from api"""
    exp = cellengine.Experiment('test_experiment')
    assert exp.name == 'test_experiment'
#   TODO: more assertions here
    assert exp._id == '5d38a6f79fae87499999a74b'
    assert type(exp._properties) is dict


@pytest.mark.vcr()
def test_list_fcsfile(experiment):
    """Tests listing files in an experiment"""
    files = experiment.files
#   TODO: more assertions here
    assert type(files) is list


@pytest.mark.vcr()
def test_list_compensations(experiment):
    """Tests retrieval of list of compensations from API"""
    comps = experiment.compensations
    assert type(comps) is list


@pytest.mark.vcr()
def test_list_gates(experiment):
    gates = experiment.gates
    gate = gates[0]
    assert type(gates) is list
    assert type(gate) is cellengine.Gate
    # Resource representation
    assert bool(ID_REGEX.match(gate.experiment_id))
    # assert gate.name == 'gui'
    assert gate.type in ['RectangleGate', 'PolygonGate', 'EllipseGate',
                         'RangeGate', 'QuadrantGate', 'SplitGate']
    # assert gate.gid == '5d67e7ab82ad01f73b78be36'
    assert type(gate.x_channel) is str
    assert type(gate.y_channel) is str
    assert type(gate.tailored_per_file) is bool
    assert gate.fcs_file_id is None
    assert gate.parent_population_id is None
    assert type(gate.model) is dict  # odd that this isn't gate.Gate.myMunch
    assert type(gate.model.label) is list
    assert gate.model.locked is False
