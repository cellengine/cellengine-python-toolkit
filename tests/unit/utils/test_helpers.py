import os
from cellengine.resources.gate import Gate
from cellengine.resources.fcsfile import FcsFile
from cellengine.utils.classes import ResourceFactory


base_url = os.environ.get("CELLENGINE_DEVELOPMENT", "https://cellengine.com/api/v1/")
