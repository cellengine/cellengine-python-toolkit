import json
from copy import deepcopy
from typing import List
from collections import defaultdict


class ComplexPopulationBuilder:
    """Build a complex population request.

    Populations are combinations of gates. You can build complex
    populations with this class using method chaining, with
    combinations of .And, .Or, .Not, and .Xor.

    Args:
        name: The name of the new population
        parent_id (optional): The population's parent population.
        terminal_gate_gid (optional):  	The GID of the gate that differentiates
            this population from its parent.

    Examples:
    # build a population of 'singlets' and either 'CD3+' or 'CD4+' or 'CD8+'
    pop = (
            ComplexPopulationBuilder("name")
            .And(["singlets", "CD3+"])
            .Or(["CD4+", "CD8+"])
            .build()
          )
    Population.create(experiment._id, pop)


    NOTE: Population names are used here for ease of discussion.
          In reality, gate GIDs are used.
    """

    def __init__(self, name, parent_id: str = None, terminal_gate_gid: str = None):
        self._name = name
        self._parent_id = parent_id
        self._terminal_gate_gid = terminal_gate_gid
        self._and = defaultdict(list)
        self._or = defaultdict(list)
        self._not = defaultdict(list)
        self._xor = defaultdict(list)

    def _make_list(self, item):
        return item if type(item) is list else [item]

    def build(self):
        payload = deepcopy(self._and)
        payload["$and"].extend([{**d} for d in [self._or, self._not, self._xor] if d])
        return {
            "name": self._name,
            "gates": json.dumps({**payload}),
            "parentId": self._parent_id,
            "terminalGateGid": self._terminal_gate_gid,
        }

    def And(self, ids: List):
        """IDs to include in the population."""
        for val in self._make_list(ids):
            self._and["$and"].append(val)
        return self

    def Or(self, ids: List):
        """Alternative IDs to include in the population."""
        for val in self._make_list(ids):
            self._or["$or"].append(val)
        return self

    def Not(self, ids):
        """IDs to exclude from the population."""
        for val in self._make_list(ids):
            self._not["$not"].append(val)
        return self

    def Xor(self, ids):
        """IDs to exclusively include in the population."""
        for val in self._make_list(ids):
            self._xor["$xor"].append(val)
        return self
