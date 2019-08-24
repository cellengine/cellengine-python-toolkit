import pytest
import cellengine
from cellengine import _helpers as h


@pytest.mark.vcr()
def test_base_list(client):
    """Test one list query deeply"""
    _id = '5d38a6f79fae87499999a74b'
    api_object = 'fcsfiles'
    url = "experiments/{0}/{1}".format(_id, api_object)
    res_list = h.base_list(url, cellengine.FcsFile, experiment_id=_id)
    res = res_list[0]
    assert type(res_list) is list
    assert [type(r) is cellengine.FcsFile for r in res_list]
    assert res._id == '5d38a7159fae87499999a74e'
    assert res.filename == 'Specimen_001_A12_A12.fcs'
    assert res.experiment_id == '5d38a6f79fae87499999a74b'
    assert res.event_count == 898


@pytest.mark.vcr()
def test_base_list_objects(client):
    """Test for all API list routes"""
    # experiments
    res = h.base_list('experiments', cellengine.Experiment)
    assert type(res) is list
    assert type(res[0]) is cellengine.Experiment

    # experiment.attachments

    # experiment.compensations
    res = h.base_list('experiments/5d38a6f79fae87499999a74b/compensations',
                      cellengine.Compensation,
                      experiment_id='5d38a6f79fae87499999a74b')

    assert type(res[0]) is cellengine.Compensation

    # experiment.fcsfiles
    res = h.base_list('experiments/5d38a6f79fae87499999a74b/fcsfiles',
                      cellengine.FcsFile,
                      experiment_id='5d38a6f79fae87499999a74b')
    assert type(res[0]) is cellengine.FcsFile

    # experiment.gates

    # experiment.populations

    # experiment.scalesets


# def result_iterator(res, key, eq):
#     return all([len(res[n][test]) == eq for n in range(0,len(r))])


def test_base_list_queries(experiment):
    """Test all standard query parameters for list routes"""
    # TODO: test queries from objects, i.e. Experiment.files(query={})
    pass
    # parameters = ['fields', 'limit', 'query', 'skip', 'sort']
    # test_queries = [
    #     ({'fields': '+_id'}, 'assert type(res) is list'),
    #     ({'fields': '-uploader'}, '[assert "uploader" not in r for r in res]'),
    #     ({'query': 'eq(eventCount, 898)'},
    #      'assert res["_id"] == "5d38a7159fae87499999a74e"')
    # ]
    # operators = ['eq', 'gt', 'lt', 'gte', 'lte', 'ne',
    #              'size', 'in', 'nin', 'all', 'and', 'or', 'elemMatch']
    # for test in test_queries:
    #     res = h.base_list('experiments', cellengine.Experiment, params=test[0])

