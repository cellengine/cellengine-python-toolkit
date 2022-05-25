# flake8: noqa
__version__ = "0.1.0"

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from cellengine.resources.attachment import Attachment
from cellengine.resources.compensation import Compensation
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.gate import (
    EllipseGate,
    Gate,
    PolygonGate,
    QuadrantGate,
    RangeGate,
    RectangleGate,
    SplitGate,
)
from cellengine.resources.plot import Plot
from cellengine.resources.population import Population
from cellengine.resources.scaleset import ScaleSet
from cellengine.utils.api_client.APIClient import APIClient
from cellengine.utils.complex_population_builder import ComplexPopulationBuilder

UNCOMPENSATED: int = 0
"""Apply no compensation."""

FILE_INTERNAL: int = -1
"""
Use the file's internal compensation matrix, if available. If not available, an
error will be returned from API requests.
"""

PER_FILE: int = -2
"""
Use the compensation assigned to each individual FCS file. Not a valid value for
`FcsFile.compensation`.
"""
