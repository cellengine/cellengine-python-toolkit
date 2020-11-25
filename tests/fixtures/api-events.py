import pytest
import pandas


@pytest.fixture(scope="session")
def events():
    return pandas.read_pickle("tests/data/events_pickle.pkl")
