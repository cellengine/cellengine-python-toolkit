# Experiments

[CellEngine API: Experiments](https://docs.cellengine.com/api/#experiments)

An `Experiment` is largely a wrapper around the CellEngine Experiment, with
getter and setter methods for writable properties and helper methods. For a
list of accessible properties, see [Properties](#properties).

Methods are available for common access and transformations on the `Experiment`.
Most methods available from the `APIClient` are available on an `Experiment`,
with the first param `experiment_id` implicitly passed as the current
experiment's ID.

## Methods

::: cellengine.resources.experiment.Experiment
    rendering:
      show_root_heading: true
      show_source: false
      show_if_no_docstring: true

## Properties
Properties are getter methods and setter methods representing the underlying
CellEngine object. Properties are the snake_case equivalent of those documented on the
[CellEngine API](https://docs.cellengine.com/api/#experiments)
otherwise noted.
