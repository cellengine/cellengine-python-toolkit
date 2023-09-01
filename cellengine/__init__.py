# flake8: noqa
__version__ = "1.0.0"

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from cellengine.resources.attachment import Attachment
from cellengine.resources.compensation import (
    Compensation,
    UNCOMPENSATED,
    FILE_INTERNAL,
    PER_FILE,
    FileCompensations,
    Compensations,
)
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.folder import Folder
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
