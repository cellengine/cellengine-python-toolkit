import cellengine
# from conftest import my_vcr


# @my_vcr.use_cassette('tests/http_cassettes/get-populations.yml')
# def test_get_populations(experiment):
#     populations = experiment.populations
#     pop = populations[0]
#     assert type(pop) is cellengine.Population
#     assert type(populations) is list
#     assert pop._id == '5d3903529fae87499999a780'
#     assert pop.experiment_id == '5d38a6f79fae87499999a74b'
#     assert pop.name == 'test (UR)'
# #   TODO: tests


# def test_create_child(population):
#     child = population.create_child()
#     assert type(child) is cellengine.Population
