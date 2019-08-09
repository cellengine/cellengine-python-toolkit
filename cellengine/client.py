import attr
from getpass import getpass
from . import session
from .experiment import Experiment
# from .fcsfile import FcsFile
# from .compensation import Compensation


@attr.s(repr=True)
class Client(object):
    '''
    A client for making API requests.

    The `requests` Session is instantiated in the global __init__,
    but it is authorized here. Thus, all other objects must be
    composed with the session from this client.

    Args:
        username: Login credential set during CellEngine registration
        password: Password for login
        token: Authentication token; may be passed instead of username and password

    Attributes:
        experiments: List all experiments on the client

    Returns:
        client: Authenticated client object
    '''
    username = attr.ib(default=None)
    password = attr.ib(default=None)
    token = attr.ib(default=None)
    session = attr.ib(session, repr=False)

    @username.validator
    def _check_username(self, attribute, value):
        #TODO
        pass

    @password.validator
    def _check_password(self, attribute, value):
        #TODO
        pass

    def __attrs_post_init__(self):
        '''Automatically send authentication'''
        if self.username is not None:
            if self.password is None:
                self.password = getpass()

            req = session.post("signin", {
                "username": self.username,
                "password": self.password
            })
            req.raise_for_status()
            self.info = req.json()
            self.token = self.info['token']

            if req.status_code == 200:
                self.info['authenticated'] = True
                print('Authentication successful.')

        elif self.token is not None:
            session.headers.update({f"Authorization", "Bearer {self.token}"})

        else:
            raise RuntimeError("Username or token must be provided")

    @property
    def experiments(self):
        '''Return a list of Experiment objects for all experiments on client'''
        return Experiment.list_all()
