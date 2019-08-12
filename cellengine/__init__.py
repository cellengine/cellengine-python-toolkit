import os
from requests_toolbelt import sessions

BASE_URL = os.environ.get('CELLENGINE_DEVELOPMENT', 'https://cellengine.com/api/v1/')
# BASE_URL = 'https://cellengine.com/api/v1/'
# BASE_URL = 'http://localhost:3000/api/v1/'

session = sessions.BaseUrlSession(base_url=BASE_URL)
# session.params = {}
# session.params['base_url'] = BASE_URL

from .client import Client
from .experiment import Experiment
from .compensation import Compensation
from .fcsfile import FcsFile
