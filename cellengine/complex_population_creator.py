cellengine = __import__(__name__.split(".")[0])
import attr
from . import _helpers
from .population import Population


def create_complex_population(experiment_id, base_gate, name, gates):
    body = {"name": name, "gates": base_gate}
    body.update(gates)
    res = _helpers.base_create(
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

class ComplexPopulationRequest:
    """Create a complex population.
    """

    def create_complex_population(
        self,
        experiment_id,
        name,
        gates,
        and_gates=None,
        or_gates=None,
        not_gates=None,
        xor_gates=None,
    ):
        complex_gates = self.complex_population_combiner(
            and_gates, or_gates, not_gates, xor_gates
        )
        body = self.complex_body(name, gates._id, complex_gates)
        res = _helpers.base_create(
            classname=Population,
            url="experiments/{0}/populations".format(experiment_id),
            json=body,
            expected_status=201,
        )
        return res

    def complex_body(self, name, gates, complex_gates):
        base = {"name": name, "gates": gates}
        base.update(complex_gates)
        return base

    def complex_population_combiner(
        self, and_gates=None, or_gates=None, not_gates=None, xor_gates=None
    ):
        all_gates = self.complex_and(and_gates).pop("$and")
        all_gates.append(self.complex_or(or_gates))
        all_gates.append(self.complex_not(not_gates))
        all_gates.append(self.complex_xor(xor_gates))
        return {"$and": [val for val in all_gates if val is not None]}

    def complex_and(self, gates):
        if gates is not None:
            return {"$and": [gate._id for gate in self.as_list(gates)]}

    def complex_or(self, gates):
        if gates is not None:
            return {"$or": [gate._id for gate in self.as_list(gates)]}

    def complex_not(self, gates):
        if gates is not None:
            return {"$not": [gate._id for gate in self.as_list(gates)]}

    def complex_xor(self, gates):
        if gates is not None:
            return {"$xor": [gate._id for gate in self.as_list(gates)]}

    def as_list(self, object):
        if type(object) is list:
            return object
        else:
            return [object]
