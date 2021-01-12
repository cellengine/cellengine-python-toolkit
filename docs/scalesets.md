# ScaleSets

[CellEngine API: ScaleSets](https://docs.cellengine.com/api/#scalesets)

A scale set is a set of scales (one scale per channel name for all channels in
the experiment). Each experiment has exactly one scale set. Uploading a file
updates the experiment's scale set to ensure that the new file's channels are
included. If a new channel must be added to a ScaleSet, the default scale from
the FCS file will be used.

It is possible to add or update scales to the scaleset. Scales are a dict of
dicts, and may be manipulated as expected:

```python
scaleset.scales["Channel-1"].update({"maximum": 10})
# or
scaleset.scales["Channel-2"]["maximum"] = 10

scaleset.scales["Channel-3"]["type"] = "ArcSinhScale"
```

## Properties
Properties are getter methods and setter methods representing the underlying
CellEngine object. Properties are the snake_case equivalent of those documented on the
[CellEngine API](https://docs.cellengine.com/api/#populations) unless otherwise noted.

## Methods

::: cellengine.resources.scaleset.ScaleSet
