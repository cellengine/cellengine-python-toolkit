# Gates

[CellEngine API: Gates](https://docs.cellengine.com/api/#gates)

Gates are geometric shapes that define boundaries within which events (cells)
must be contained to be considered part of a population. Each gate type has its
own implementation of the abstract ``Gate`` class. Do not instantiate the base
``Gate`` class directly.

All gate types share some required and optional arguments,
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
Properties are the snake_case equivalent of those documented on the
[CellEngine API](https://docs.cellengine.com/api/#gates) unless otherwise noted.

## Gate Models

Gates have a `model` property, which is a nested `dict` object. For
convenience, the `model` property has dot-indexing for getting and setting
properties. For instance:

```python
> gate = experiment.gates[0]
> gate.model
Munch({'polygon': Munch({'vertices': [[4.68957, 2.90929], [5.23152, 5.77464], [7.76064, 5.956], [8.59164, 4.65026], [6.71287, 2.32896]]}), 'locked': 'orange', 'label': [7.62844, 6.19701]})

> gate.model.polygon.vertices
[[4.68957, 2.90929],
 [5.23152, 5.77464],
 [7.76064, 5.956],
 [8.59164, 4.65026],
 [6.71287, 2.32896]]
```

You can set the values of these properties. You must explicitly call the
`update` method for these changes to be saved to CellEngine.
```python
> gate.model.locked
True

> gate.model.locked = False
> gate.update()
> gate.model.locked
False
```

You may set invalid values, but `update` will fail with an API error:
```python
> gate.model.locked = "orange"
> gate.model.locked
"orange"

> gate.update()
APIError: CellEngine API: status code 400 != 200 for URL
https://cellengine.com/api/v1/experiments/.../gates/...
-- "locked" must be a Boolean.
```

## Creating Gates
Gates may be created singly or in bulk.

#### Create a single new gate using kwargs:
```python
# using a method on Experiment
exp.create_ellipse_gate(
    x_channel="FSC-A",
    y_channel="FSC-W",
    name="my gate",
    x=260000,
    y=64000,
    angle=0,
    major=120000,
    minor=70000
    )

# using a classmethod
from cellengine import EllipseGate
gate = EllipseGate.create(
    experiment_id=exp._id,
    # the same kwargs
    )
gate.post()
```

#### Post gates in bulk

When creating many gates, it will be _much_ more efficient to build the gates
in a list, then save them in bulk to CellEngine. For instance:
```python
gates = []
gates.append(
    EllipseGate.create(
        experiment_id=exp._id,
        # args, kwargs
        )
    )
gates.append(
    RectangleGate.create(
        experiment_id=exp._id,
        # args, kwargs
        )
    )

Gate.bulk_create(gates)
# returns [EllipseGate(...), RectangleGate(...)]
```
