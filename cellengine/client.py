from typing import List, Optional
import attr
from getpass import getpass
from cellengine import session
from cellengine.utils import helpers
from cellengine.utils.loader import Loader
from cellengine.resources.experiment import Experiment


@attr.s(repr=True)
class Client(object):
    """A client for making API requests.

    There are three ways of authenticating:
        1. Username and password. Use this to authenticate a user.
        2. API token. Use this to authenticate an application that is
            not associated with a user, such as a LIMS integration.
        3. Auto-authorization. If you are running a Jupyter CellEngine
            session, you will be automatically authorized as your
            user account.

    Args:
        username: Login credential set during CellEngine registration
        password: Password for login
        token: Authentication token; may be passed instead of username and password

    Attributes:
        experiments: List all experiments on the client

    Returns:
        client: Authenticated client object
    """

    username = attr.ib(default=None)
    password = attr.ib(default=None, repr=False)
    token = attr.ib(default=None, repr=False)
    _session = attr.ib(session, repr=False)

    def __attrs_post_init__(self):
        """Automatically send authentication"""
        if self.username is not None:
            if self.password is None:
                self.password = getpass()

            req = self._session.post(
                "signin", {"username": self.username, "password": self.password}
            )
            req.raise_for_status()

            if req.status_code == 200:
                print("Authentication successful.")

        elif self.token is not None:
            self._session.cookies.update({"token": "{0}".format(self.token)})

        else:
            raise RuntimeError("Username or token must be provided")

    def get_experiment(self, _id: Optional[str] = None, name: Optional[str] = None) -> Experiment:
        return Loader.get_experiment(_id=_id, name=name)

    @property
    def experiments(self) -> List[Experiment]:
        """Return a list of Experiment objects for all experiments on client"""
        return helpers.base_list("experiments", Experiment)
