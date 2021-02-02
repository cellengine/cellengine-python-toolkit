# Compensations

[CellEngine API: Compensations](https://docs.cellengine.com/api/#compensations)

A compensation is a list of channel names and a corresponding square matrix.
The matrix is technically a "spill" or "spillover" matrix, which is inverted to
yield the compensation matrix; most applications refer to the spill matrix as a
compensation matrix, however.

In the Python SDK, the matrix is represented by a Pandas DataFrame.

## Properties
Properties are getter methods and setter methods representing the underlying
CellEngine object. Properties are the snake_case equivalent of those documented
on the [CellEngine API](https://docs.cellengine.com/api/#compensations) unless
otherwise noted.

## Methods

::: cellengine.resources.compensation.Compensation
    rendering:
      show_if_no_docstring: true
