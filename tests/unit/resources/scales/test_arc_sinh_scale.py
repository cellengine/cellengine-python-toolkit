import pytest
from math import isclose
from numpy import arcsinh
from pandas import Series

from cellengine.utils.scale_utils import apply_scale


@pytest.fixture(scope="module")
def scale():
    return {"minimum": -200, "maximum": 5000, "cofactor": 5, "type": "ArcSinhScale"}


def test_should_apply_scale(scale):
    # fmt: off
    input = Series([
        -250, -20, -2, -0.01, 0, 0.2, 0.5, 1,
        5, 10, 100, 500, 1000, 5000, 10000, 50000
            ])
    # fmt: on
    output = Series([], dtype="float64")
    output = input.map(lambda a: apply_scale(scale, a, False))

    # fmt: off
    expected = [
        -4.605270170991424, -2.0947125472611012, -0.3900353197707155,
        -0.0019999986666690665, 0, 0.03998934100602701, 0.09983407889920756,
        0.19869011034924142, 0.8813735870195429, 1.4436354751788103,
        3.689503868988906, 5.298342365610589, 5.991470797049389,
        7.600902709541988, 8.294049702602022, 9.903487555036127
    ]
    # fmt: on
    assert [isclose(a, b, rel_tol=0.00001) for a, b in zip(output, expected)]


def test_should_apply_clamped(scale):
    # fmt: off
    input = Series([
        -250, -20, -2, -0.01, 0, 0.2, 0.5,  1, 5,
        10, 100, 500, 1000, 5000, 10000, 50000
    ])
    # fmt: on
    output = Series([], dtype="float64")
    output = input.map(lambda a: apply_scale(scale, a, True))
    # fmt: off
    expected = [
        -4.382182848065498, -2.0947125472611012, -0.3900353197707155,
        -0.0019999986666690665, 0, 0.03998934100602701, 0.09983407889920756,
        0.19869011034924142, 0.8813735870195429, 1.4436354751788103,
        3.689503868988906, 5.298342365610589, 5.991470797049389,
        7.600902709541988, 7.600902709541988, 7.600902709541988
    ]
    # fmt: on
    assert [isclose(a, b, rel_tol=0.00001) for a, b in zip(output, expected)]


def test_should_handle_0_length_arrays(scale):
    input = Series([], dtype="float64")
    output = Series([], dtype="float64")
    output = input.map(lambda a: apply_scale(scale, a, True))
    assert type(output) is Series
    assert output.size == 0


def test_correctly_applies_scale_of_length_n(scale):
    for n in range(1, 32):
        input = Series([1] * n)
        output = Series([], dtype="float64")
        output = input.map(lambda a: apply_scale(scale, a, True))
        for i in range(0, n):
            assert isclose(output[i], arcsinh(1 / scale["cofactor"]), rel_tol=0.00001)
