from math import isclose
from numpy import array
from cellengine.utils.helpers import normalize


def test_normalizes_single_value_to_range():
    # Given
    rmin = 1
    rmax = 10
    range = [10, 20, 40]

    # When
    x = normalize(15, min(range), max(range), rmin, rmax)

    # Then
    assert x <= 10
    assert x >= 1


def test_normalizes_values_to_range():
    # Given
    rmin = 1
    rmax = 10
    range = array([10, 40])

    # When
    x, y = normalize(range, range.min(), range.max(), rmin, rmax)

    # Then
    assert isclose(x, rmin)
    assert isclose(y, rmax)


def test_normalizes_negative_values_to_range():
    # Given
    vals = array([[262144, 262144], [-200, 262144], [-200, -200], [262144, -200]])

    # When
    x = normalize(vals, vals.min(), vals.max(), 0, 290)

    # Then
    assert x.min() == 0
    assert x.max() == 290

    assert (x == array([[290.0, 290.0], [0.0, 290.0], [0.0, 0.0], [290.0, 0.0]])).all()


def test_denormalizes_values_to_original_range():
    # Given
    vals = array(
        [
            [262144, 262144],
            [-200, 262144],
            [-200, -200],
            [262144, -200],
            [261944, 10000],
        ]
    )

    # When
    normalized = normalize(vals, vals.min(), vals.max(), 0, 290)
    denormalized = normalize(normalized, 0, 290, vals.min(), vals.max())

    # Then
    assert (denormalized.astype(int) == vals).all()
