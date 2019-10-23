cellengine = __import__(__name__.split(".")[0])
import attr
from . import helpers
from .population import Population


def create_complex_population(experiment_id, base_gate, name, gates):
    body = {"name": name, "gates": base_gate}
    body.update(gates)
    res = helpers.base_create(
        classname=Population,
        url="experiments/{0}/populations".format(experiment_id),
        json=body,
        expected_status=201,
    )
    return res


@attr.s
class And:
    gates = attr.ib()
    other_gates = attr.ib(default=None)

    def formatted(self):
        and_gates = {"$and": [self.gates]}
        all_gates = and_gates.update(self.other_gates)
        return all_gates
