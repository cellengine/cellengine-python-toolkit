import pytest
from math import isclose
from numpy import log10
from pandas import Series

from cellengine.payloads.scale_utils.apply_scale import apply_scale


@pytest.fixture(scope="module")
def scale():
    return {"minimum": 5, "maximum": 10, "type": "LogScale"}


def test_should_apply_scale(scale):
    # fmt: off
    input = Series([
        -20, 0, 1e-40, 0.01, 0.2, 0.5, 0.9999, 1, 1.00001,
        2, 5, 10, 100, 250, 500, 1000, 5000, 10000, 50000,
        5e5, 5e6, 5e7, 5e8, 5e9, 5e10, 5e11, 5e12, 5e13, 5e14,
        5e15, 5e16, 5e17
    ])
    # fmt: on
    output = Series([])
    output = input.map(lambda a: apply_scale(scale, a, False))
    # fmt: off
    expected = Series([
        0, 0, 0, 0, 0, 0, 0, 0, 0.00000434292310445319, 0.30102999566398114,
        0.6989700043360186, 1, 2, 2.397940008672037, 2.6989700043360183, 3,
        3.6989700043360187, 4, 4.698970004336018, 5.698970004336018,
        6.698970004336018, 7.698970004336018, 8.698970004336018,
        9.698970004336018, 10.698970004336018, 11.698970004336018,
        12.698970004336018, 13.698970004336018, 14.698970004336018,
        15.698970004336018, 16.698970004336018, 17.698970004336018,
    ])
    # fmt: on
    assert [isclose(a, b, rel_tol=0.00001) for a, b in zip(output, expected)]


def test_should_apply_clamped(scale):
    # fmt: off
    input = Series([
        -20, 0, 0.01, 0.2, 0.5, 1, 2, 5, 10,
        100, 250, 500, 1000, 5000, 10000, 50000
    ])
    # fmt: on
    output = Series([])
    MINV = 0.6989700043360186
    MAXV = 1
    output = input.map(lambda a: apply_scale(scale, a, True))
    # fmt: off
    expected = Series([
        MINV, MINV, MINV, MINV, MINV, MINV, MINV,
        0.6989700043360186, 1, MAXV, MAXV, MAXV,
        MAXV, MAXV, MAXV, MAXV,
    ])
    # fmt: on
    assert [isclose(a, b, rel_tol=0.00001) for a, b in zip(output, expected)]


def test_should_handle_0_length_arrays(scale):
    input = Series([])
    output = Series([])
    output = input.map(lambda a: apply_scale(scale, a, True))
    assert type(output) is Series
    assert output.size == 0


def test_correctly_applies_scale_of_length_n(scale):
    for n in range(1, 32):
        input = Series([1] * n)
        output = Series([])
        output = input.map(lambda a: apply_scale(scale, a, True))
        for i in range(0, n):
            assert isclose(output[i], log10(scale["minimum"]), rel_tol=0.00001)
