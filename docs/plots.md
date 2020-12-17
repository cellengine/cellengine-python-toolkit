# Plots

[CellEngine API: Plots](https://docs.cellengine.com/api/#plots)

A `Plot` is largely a wrapper around the CellEngine Plot, with
getter and setter methods for writable properties and helper methods. For a
list of accessible properties, see [Properties](#properties).

Methods are available for common access and transformations on the `Plot`.

## Methods

::: cellengine.resources.plot.Plot
    selection:
      members:
        - display
        - get
        - save

## Properties
The Python SDK `Plot` only has accessible `display`, `get`, and `save` methods.
In the case of `Plot`, `properties` refers to an optional dictionary of
configuration arguments to pass to the `get` method. Options are detailed
above.
