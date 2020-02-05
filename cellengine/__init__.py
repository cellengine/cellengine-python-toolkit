import os
import requests
from requests_toolbelt import sessions

BASE_URL = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")
global ID_INDEX
ID_INDEX = 0


session = sessions.BaseUrlSession(base_url=BASE_URL)
session.headers.update(
    {
        "User-Agent": "CellEngine Python API Toolkit/0.1.1 requests/{0}".format(
            requests.__version__
        )
    }
)

from .client import Client
from .resources.experiment import Experiment
from .resources.population import Population
from .resources.compensation import Compensation
from .resources.fcsfile import FcsFile
from .resources.attachments import Attachment
from .resources.gate import (
    Gate,
    RectangleGate,
    PolygonGate,
    EllipseGate,
    QuadrantGate,
    SplitGate,
    RangeGate,
)


from .utils.loader import by_name

cache_info = by_name.cache_info
clear_cache = by_name.cache_clear
