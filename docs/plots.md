# Plots

[CellEngine API: Plots](https://docs.cellengine.com/api/#plots)

A `Plot` is an image representing of cytometry data.

## Properties
The Python SDK `Plot` only has `display`, `get`, and `save` methods. In the case
of `Plot`, `properties` refers to an optional dictionary of configuration
arguments to pass to the `get` method. Options are detailed above.

## Methods

::: cellengine.resources.plot.Plot
    selection:
      members:
        - display
        - get
        - save
