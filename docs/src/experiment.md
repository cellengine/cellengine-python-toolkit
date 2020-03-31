# Experiments

[CellEngine API: Experiments](https://docs.cellengine.com/api/#experiments)

An Experiment is largely a wrapper around the CellEngine Experiment, with
getter and setter methods for writable properties and helper methods. For a
list of accessible properties, see [Properties](#properties).

Methods are available for common access and transformations on the Experiment.

## Methods

::: cellengine.resources.experiment.Experiment
    rendering:
      show_root_heading: true
      show_source: false
      show_if_no_docstring: true
    selection:
      members:
        - files
        - get_fcsfile
        - populations
        - compensations
        - gates
        - attachments
        - update
        - delete_gates
        - create_rectangle_gate
        - create_polygon_gate
        - create_ellipse_gate
        - create_range_gate
        - create_split_gate
        - create_quadrant_gate
        - create_complex_population

## Properties
Properties are getter methods and setter methods representing the underlying
CellEngine object. Properties are the snake_case equivalent of those documented on the
[CellEngine API](https://docs.cellengine.com/api/#experiments)
otherwise noted.
