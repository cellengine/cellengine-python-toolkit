# Gates

[CellEngine API: Gates](https://docs.cellengine.com/api/#gates)

A Gate is a wrapper around the CellEngine Gate object, with getter and
setter methods for writable properties and helper methods. Each gate type has
its own implementation of the abstract ``Gate`` class. Do not instantiate the
base ``Gate`` class directly.

When creating gates, all gate types share some required and optional arguments,
which are [documented][cellengine.resources.gate.Gate] on the base ``Gate``
class. Gate-specific arguments are documented in each gate type.

For a list of accessible properties, see [Properties](#properties).

Methods are available for common access and transformations on the Gate.

## Gate ABC and Methods

Although you should not instantiate the `Gate` class, each gate type will
inherit the methods below.

::: cellengine.resources.gate.Gate
    rendering:
      show_root_heading: true
      show_source: false
      show_if_no_docstring: true
    selection:
      members:
        - get
        - build
        - update
        - delete
        - post
        - delete_gates

## Gate Types

::: cellengine.resources.gate.RectangleGate

::: cellengine.resources.gate.PolygonGate

::: cellengine.resources.gate.EllipseGate

::: cellengine.resources.gate.RangeGate

::: cellengine.resources.gate.SplitGate

::: cellengine.resources.gate.QuadrantGate

## Properties
Properties are getter methods and setter methods representing the underlying
CellEngine object. Properties are the snake_case equivalent of those documented on the
[CellEngine API](https://docs.cellengine.com/api/#gates) unless otherwise
noted.
