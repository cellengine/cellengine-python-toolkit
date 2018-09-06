# Copyright 2018 Primity Bio
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
import getpass
from .experiment import Experiment

class Client(object):
    """Client used to make API requests.

    There are three ways of authenticating:
    1. Username and password. Use this to authenticate as a user.
    2. API token. Use this to authenticate an application that is not associated
      with a user, such as a LIMS integration.
    3. Auto-authorization. If you are running a Jupyter CellEngine session, then
      you will be automatically authorized as your user account.

    :type username: str or None :param username: (Optional) The username of the
    user to authenticate as.

    :type password: str or None :param password: (Optional) If ``username`` is
    provided and ``password`` is not, an interactive prompt will be displayed to
    collect your password.

    :type token: str or None :param token: (Optional) An API token.

    .. versionadded:: 0.1
    """

    def __init__(self, username=None, password=None, token=None):
        self._s = requests.Session()

        if username is not None:
            if password is None:
                password = getpass.getpass()
            req = self._s.post("https://cellengine.com/api/v1/signin", {
                "username": username,
                "password": password
            })
            req.raise_for_status()

        elif token is not None:
            self._s.headers.update({"Authorization", "Bearer: {0}".format(token)})

        else:
            raise RuntimeError("username or token must be provided")

    def get_experiment(self, name=None, _id=None):
        """Get an experiment by name or _id.

        If you pass an unnamed argument, this method will attempt to
        automatically detect if the value is the name or _id. In the unlikely
        case that you have an experiment name that looks like an _id, use the
        ``name`` argument explicitly.

        Example:

            client.get_experiment("My experiment")
        """
        experiment = Experiment(self, name, _id)
        experiment.load()
        return experiment

    def list_experiments(self, limit=None, fields=None):
        pass
