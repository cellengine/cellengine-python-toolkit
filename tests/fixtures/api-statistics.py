import pytest


@pytest.fixture(scope='session')
def statistics():
    statistics = [
        {
            "fcsFileId": "5d64abe2ca9df61349ed8e79",
            "filename": "Specimen 01.fcs",
            "populationId": "2d64abe2ca9df61348ed8z9b",
            "population": "Singlets",
            "uniquePopulationName": "Singlets",
            "parentPopulationId": None,
            "parentPopulation": "Ungated",
            "channel": "PE-A",
            "reagent": "CD3",
            "mean": 52040.376758718616,
            "median": 50881.291015625,
            "quantile": 51616.5477815448,
        },
        {
            "fcsFileId": "5d64abe2ca9df61349ed8e7a",
            "filename": "Specimen 01.fcs",
            "populationId": "2d64abe2ca9df61348ed8z9a",
            "population": "Singlets",
            "uniquePopulationName": "Singlets",
            "parentPopulationId": None,
            "parentPopulation": "Ungated",
            "channel": "FSC-A",
            "mean": 87881.26381655093,
            "median": 86734.2890625,
            "quantile": 87800.75920644606,
        },
    ]
    return statistics
