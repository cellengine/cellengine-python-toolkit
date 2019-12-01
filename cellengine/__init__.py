import os
import requests
from requests_toolbelt import sessions

BASE_URL = os.environ.get('CELLENGINE_DEVELOPMENT', 'https://cellengine.com/api/v1/')
ID_INDEX = 0

session = sessions.BaseUrlSession(base_url=BASE_URL)
session.headers.update({'User-Agent': "CellEngine Python API Toolkit/0.1.1 requests/{0}".format(requests.__version__)})

from .client import Client
from .experiment import Experiment
from .population import Population
from .compensation import Compensation
from .fcsfile import FcsFile
from .gate import Gate
