import vcr
import pytest
import cellengine
from conftest import fixture_vcr


@pytest.fixture(scope='session')
def experiment(client, setup_teardown):
    """Returns an experiment for testing"""
    with fixture_vcr.use_cassette('tests/cassettes/experiment.yaml'):
        experiment = cellengine.Experiment(name='pytest')
        experiment.create_rectangle_gate('FSC-A', 'FSC-W', 'fcs_rect_gate',
                                         x1=1, x2=2, y1=3, y2=4,
                                         fcs_file='Specimen_001_A1_A01.fcs',
                                         tailored_per_file=False)
        return experiment
