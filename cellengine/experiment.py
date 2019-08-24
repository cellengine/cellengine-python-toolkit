import attr
from .client import session
from . import _helpers
from .fcsfile import FcsFile
from .compensation import Compensation


@attr.s
class Experiment(object):
    """A class representing a CellEngine experiment.

    Attributes
        name (:obj:`str`, optional):   Name of the experiment; can be queried
        _id (:obj:`str`, optional):    Experiment ID; can be queried in place of `name`
        _properties (:obj:`dict`, optional): Experiment properties; loaded automatically.
    """
    name = attr.ib(default=None)
    _id = attr.ib(default=None)
    _properties = attr.ib(default={}, repr=False)
    _session = attr.ib(default=session, repr=False)

    def __attrs_post_init__(self):
        """Load automatically by name or by id"""
        _helpers.load(self, self.path)  # from _helpers

    @staticmethod
    def list_all():
        """Returns a list of all accesible experiments"""
        res = session.get('experiments')
        res.raise_for_status()
        exps = [Experiment(id=item['_id'], properties=item) for item in res.json()]
        return exps

    @property
    def files(self):
        """List all files on the experiment"""
        url = "experiments/{0}/fcsfiles".format(self._id)
        return _helpers.base_list(url, FcsFile, experiment_id=self._id)

    @property
    def populations(self):
        """List all populations in the experiment"""
        pass
        # url = "experiments/{0}/populations".format(self._id)
        # return _helpers.base_list(url, Population, experiment_id=self._id)

    @property
    def compensations(self):
        url = "experiments/{0}/compensations".format(self._id)
        return _helpers.base_list(url, Compensation, experiment_id=self._id)

    @property
    def gates(self):
        pass
        # url = "experiments/{0}/gates".format(self._id)
        # return _helpers.base_list(url, Gate, experiment_id=self._id)

    @property
    def path(self):
        base_path = 'experiments'
        if self._id is not None:
            return "{0}/{1}".format(base_path, self._id)
        else:
            return "{0}".format(base_path)

    @property
    def comments(self):
        comments = self._properties['comments']
        if type(comments) is not _helpers.CommentList:
            self._properties['comments'] = _helpers.CommentList(comments)
        return comments

    @comments.setter
    def comments(self, comments):
        """Sets comments for experiment.

        Defaults to overwrite; append new comments with
        experiment.comments.append(dict) with the form:
         dict = {"insert": "some text",
        "attributes": {"bold": False, "italic": False, "underline": False}}.
        """
        if comments.get('insert').endswith('\n') is False:
            comments.update(insert=comments.get('insert')+'\n')
        self._properties['comments'] = comments

    @property
    def updated(self):
        return timestamp_to_datetime(self._properties.get('updated'))

    @property
    def deep_updated(self):
        return _helpers.timestamp_to_datetime(self._properties.get('deepUpdated'))

    @property
    def deleted(self):
        if self._properties.get('deleted') is not None:
            return _helpers.timestamp_to_datetime(self._properties.get('deleted'))

    @property
    def delete(self):
        """Marks the experiment as deleted.

        Deleted experiments are permanently deleted after approximately
        7 days. Until then, deleted experiments can be recovered.
        """
        self._properties['deleted'] = _helpers.today_timestamp()

    public = _helpers.GetSet('public')

    uploader = _helpers.GetSet('uploader')

    primary_researcher = _helpers.GetSet('primaryResearcher')

    active_compensation = _helpers.GetSet('activeCompensation')

    locked = _helpers.GetSet('locked')

    clone_source_experiment = _helpers.GetSet('cloneSourceExperiment')

    revision_source_experiment = _helpers.GetSet('revisionSourceExperiment')

    revisions = _helpers.GetSet('revisions')

    per_file_compensations_enabled = _helpers.GetSet('perFileCompensationsEnabled')

    tags = _helpers.GetSet('tags')

    annotation_name_order = _helpers.GetSet('annotationNameOrder')

    annotation_tabe_sort_columns = _helpers.GetSet('annotationTableSortColumns')

    permissions = _helpers.GetSet('permissions')

    created = _helpers.GetSet('created')
