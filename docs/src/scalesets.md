# ScaleSets

[CellEngine API: ScaleSets](https://docs.cellengine.com/api/#populations)

A scale set is a set of scales (one scale per channel name for all channels in
the experiment). Each experiment has exactly one scale set. Uploading a file
updates the experiment's scale set to ensure that the new file's channels are
included. If a new channel must be added to a ScaleSet, the default scale from
the FCS file will be used.

Currently, ScaleSets are a raw Dict.

