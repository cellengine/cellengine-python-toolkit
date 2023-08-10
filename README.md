CellEngine Python API Toolkit
-----

A Python interface for the CellEngine API that enables you to securely,
reproducibly and easily interact with your data from a Python or Jupyter
environment.

Please refer to [Python Toolkit Documentation](https://primitybio.github.io/cellengine-python-toolkit/)
and [CellEngine API Documentation](https://docs.cellengine.com/api/) for more information.

## Upcoming v1.0.0 release (master branch)

v1.0.0 will be the first stable release of the CellEngine Python Toolkit.

### Breaking changes

* **`path` property removed.** Previously, all classes had a `path` property
  that was the URL of the resource. This conflicted with the `path` property of
  Folders and Experiments.

* **`FcsFile.header` is now a dict.** Previously this was a JSON string. For
  convenience, it's now pre-parsed into a dict.

* **Events DataFrames now consistently use a multi-level index** with the first
  level being the channel name and the second level being the reagent name. This
  applies to the return values of `FcsFile.get_events()`, `Compensation.apply()`
  and `ScaleSet.apply()`.

* **`Experiment.get_statistics()` return type defaults to DataFrame.**
  Previously it was a dict.

* **`Cls.from_dict()` and `Cls.to_dict()` have been removed.** These were meant
  for internal use and are no longer necessary.

* **`RangeGate`, `RectangleGate`, `PolygonGate` and `EllipseGate` now inherit
  from `SimpleGate`, and `QuadrantGate` and `SplitGate` now inherit from
  `CompoundGate`.** This means that simple gates no longer have a `names`
  property and compound gates no longer have a `name` property.

* **`Experiment.scalesets` is now `Experiment.scaleset` and
  `Experiment.get_scaleset()` takes no args.** There is only one ScaleSet in an
  experiment, so passing an `_id` or name is unnecessary.

### Additional improvements

* Most dependencies have been removed.
* MyPy types have been significantly improved.
* Support for `Experiment.path` property was added.
* Support for `compensation` in the `Experiment.plot()` method was added.
* `Cls.update()` now only sends changed values to CellEngine. This reduces the
  permissions required for some operations.
* All tests now run against a real CellEngine instance instead of using mocks,
  avoiding bugs due to stale mocks.
