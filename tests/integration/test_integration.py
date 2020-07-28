import logging
import pytest
import cellengine


log = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def client():
    return cellengine.APIClient("gegnew", "testpass123")

@pytest.fixture(scope='module')
def setup_experiment(request, client):
    log.info("Setting up CellEngine experiment for {}".format(__name__))
    exp = cellengine.Experiment.create("new_experiment")
    exp.upload_fcs_file("tests/data/Acea - Novocyte.fcs")

    def teardown():
        log.info("Starting teardown of: {}".format(__name__))
        client.delete_experiment(exp._id)
    request.addfinalizer(teardown)


class TestCellenginePythonToolkitIntegration:

    def test_should_do_something(self, setup_experiment, client):
        self.experiment = client.get_experiment(name="new_experiment")
        assert "new_experiment" == self.experiment.name
