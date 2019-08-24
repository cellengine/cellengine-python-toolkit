import pytest
import pandas


@pytest.mark.vcr()
def test_compensation(experiment):
    """Tests a compensation's properties"""
    comp = experiment.compensations[0]
    print(type(comp.dataframe))
    assert type(comp.dataframe) is pandas.core.frame.DataFrame
    assert all(comp.dataframe.index == comp.channels)
    assert comp.N == len(comp.dataframe)
