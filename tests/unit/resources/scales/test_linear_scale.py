import pytest
from pandas import Series

from cellengine.payloads.scale_utils.apply_scale import apply_scale


@pytest.fixture(scope="module")
def scale():
    scale = {"minimum": 5, "maximum": 10, "type": "LinearScale"}
    return scale


def test_should_apply_scale(scale):
    input = Series([10, 0, 1.2, 10, 40])
    output = Series([])
    output = input.map(lambda a: apply_scale(scale, a, False))
    assert all(output == Series([10, 0, 1.2, 10, 40]))


def test_should_apply_clamped(scale):
    input = Series([10, 7, 1.2, 9, 40])
    output = Series([])
    output = input.map(lambda a: apply_scale(scale, a, True))
    assert all(output == ([10, 7, 5, 9, 10]))


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
        assert all(output == Series([scale["minimum"]] * n))
