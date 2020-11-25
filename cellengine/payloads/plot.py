import attr


@attr.s
class _Plot:
    """A class containing CellEngine population resource properties."""

    experiment_id = attr.ib()

    fcs_file_id = attr.ib()

    x_channel = attr.ib()

    y_channel = attr.ib()

    plot_type = attr.ib()

    population_id = attr.ib()

    data = attr.ib(repr=False)
