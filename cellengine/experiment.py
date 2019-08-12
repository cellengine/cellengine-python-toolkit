import attr
from .client import session
from ._helpers import load, created
from .fcsfile import FcsFile
from .compensation import Compensation


@attr.s()
class Experiment(object):
   """A class representing a CellEngine experiment.

    Attributes
        name (:obj:`str`, optional):   Name of the experiment; can be queried
        _id (:obj:`str`, optional):    Experiment ID; can be queried in place of `name`
        query (:obj:`str`, optional):  Query for loading. Defaults to "name"
        _properties (:obj:`dict`, optional): Experiment properties. This is loaded automatically.
        session: Authenticated session for the client. No reason to change this.
    """

    name = attr.ib(default=None)
    _id = attr.ib(default=None)
    query = attr.ib(default="name", repr=False)
    _properties = attr.ib(default={}, repr=False)
    session = attr.ib(default=session, repr=False)

    def __attrs_post_init__(self):
        """Load automatically by name or by id"""
        load(self, self.path)  # from _helpers

    @staticmethod
    def list_all():
        """Return a list of Experiment objects for all experiments on client"""
        res = session.get('experiments')
        res.raise_for_status()
        exps = [Experiment(id=item['_id'], properties=item) for item in res.json()]
        return exps

    @property
    def files(self):
        """List all files on the experiment"""
        return FcsFile.list(self._id, query=self.query)

#   TODO: settermethod for files as method of uploading files to experiment?

    @property
    def compensations(self):
        return Compensation.list(self._id)

    @property
    def path(self):
        base_path = 'experiments'
        if self._id is not None:
            return f"{base_path}/{self._id}"
        else:
            return f"{base_path}"

    @property
    def comments(self):
        return self._properties.get("comments")

    @comments.setter
    def comments(self, comments):
        """Sets comments for experiment. Defaults to overwrite;
        append new comments with experiment.comments.append(dict)
        with the form: dict = {"insert": "some text",
        "attributes": {"bold": False, "italic": False, "underline": false}}.
        """
        self._properties['comments'] = comments

    @property
    def updated(self):
        return timestamp_to_datetime(self._properties.get('updated'))

    @property
    def deep_updated(self):
        return timestamp_to_datetime(self._properties.get('deepUpdated'))

    @property
    def deleted(self):
        if self._properties.get('deleted') is not None:
            return timestamp_to_datetime(self._properties.get('deleted'))

    @property
    def delete(self):
        """Marks this experiment as deleted. Deleted experiments are permanently
        deleted after approximately 7 days. Until then, deleted experiments can
        be recovered.
        """
        self._properties['deleted'] = today_timestamp()
        print('Experiment flagged for deletion.')

    @property
    def public(self):
        return self._properties.get('public')

    @public.setter
    def public(self, public):
        self._properties['public'] = public

    # uploader

    # primaryResearcher

    # activeCompensation

    @property
    def locked(self):
        return self._properties.get('locked')

    @property
    def clone_source_experiment(self):
        return self._properties.get("cloneSourceExperiment", None)

    @property
    def revision_source_experiment(self):
        return self._properties.get('revisionSourceExperiment', None)

    # revisions

    @property
    def per_file_compensations_enabled(self):
        return self._properties.get("perFileCompensationsEnabled")

    @property
    def tags(self):
        return self._properties.get("tags")

    # annotationNameOrder

    # annotationTableSortColumns

    # permissions

    @property
    def created(self):
        return created(self)
