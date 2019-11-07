import pytest
import pandas
import cellengine


def test_compensation(client):
    """Tests a compensation's properties"""
    exp = cellengine.Experiment(name='test_experiment')
    comp = exp.compensations[0]
    assert type(comp) is cellengine.Compensation
    assert type(comp.dataframe) is pandas.core.frame.DataFrame
    assert all(comp.dataframe.index == comp.channels)
    assert comp.N == len(comp.dataframe)
