import attr

cellengine = __import__(__name__.split(".")[0])
from functools import lru_cache
from cellengine import helpers


@lru_cache(maxsize=None)
def by_name(path, query, name):
    """Look up an item by name and cache it's ID for future requests."""
    url = '{0}?query=eq({1},"{2}")&limit=2'.format(path, query, name)
    content = handle_response(helpers.base_get(url))
    return content["_id"]


def handle_response(response):
    if type(response) is list:
        handle_list(response)
    else:
        response = [response]
    return response[0]


def handle_list(response):
    if len(response) == 0:
        raise RuntimeError("No objects found.")
    elif len(response) > 1:
        raise RuntimeError("Multiple objects found; use _id to query instead.")


@attr.s
class Loader(object):
    """Allows specifying a resource by name instead of by id.

    Internally, this looks up the resource's id by name before the function runs.
    Therefore, the first time an object is requested by name, two requests are
    made. To improve performance, the resource's id is then cached and a
    subsequent request is made with the id rather than the name.

    Resources such as files that exist within an experiment are cached within
    the experiment's scope. That is, the following is safe, even though the FCS
    files have the same name:

    exp.get_fcsfile(name="fcsfile1.fcs")
    exp2.get_fcsfile(name="fcsfile1.fcs")
    """

    _id = attr.ib(kw_only=True, default=None)
    name = attr.ib(kw_only=True, default=None)
    classname = attr.ib(init=True, default=None)
    query = attr.ib(init=True, default="name")
    path = attr.ib(init=True, default="experiments")

    def load(self):
        if self._id:
            return self.load_by_id()
        if self.name:
            return self.load_by_name()

    def load_by_id(self):
        content = helpers.base_get("/".join([self.path, self._id]))
        return helpers.make_class(self.classname, content)

    def load_by_name(self):
        content = self.lookup_and_cache_id(self.path, self.query, self.name)
        return helpers.make_class(self.classname, content)

    def lookup_and_cache_id(self, path, query, name):
        _id = by_name(path, query, name)
        url = "/".join([path, _id])
        return helpers.base_get(url)

    def lookup_item_by_query(self, path, query, name):
        url = '{0}?query=eq({1},"{2}")&limit=2'.format(path, query, name)
        return helpers.base_get(url)

    @staticmethod
    def get_fcsfile(experiment_id, _id, name):
        fcs_loader = Loader(
            id=_id,
            name=name,
            query="filename",
            path="experiments/{0}/fcsfiles".format(experiment_id),
            classname="cellengine.FcsFile",
        )
        return fcs_loader.load()

    @staticmethod
    def get_experiment(_id, name):
        loader = Loader(id=_id, name=name, classname="cellengine.Experiment")
        return loader.load()
