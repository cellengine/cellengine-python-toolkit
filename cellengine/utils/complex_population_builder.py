import attr
import json
from copy import deepcopy
from cellengine.utils import helpers
from cellengine.resources.population import Population
from typing import List
from collections import defaultdict

import cellengine as ce


class ComplexPopulationBuilder:
    """Build a complex population request.

    Populations are combinations of gates. You may build complex
    populations with this class using method chaining, with
    combinations of `.And`, `.Or`, `.Not`, and `.Xor`.

    Args:
        base_gate (list or str): The gate on which to base the complex population.

    Examples:
    # build a population of 'singlets' and 'CD3+' OR 'CD4+' OR 'CD8+'
    ComplexPopulationBuilder(
    """

    def __init__(self, name):
        self._name = name
        self._and = defaultdict(list)
        self._or = defaultdict(list)
        self._not = defaultdict(list)
        self._xor = defaultdict(list)

    def _make_list(self, item):
        return item if type(item) is list else [item]

    def build(self):
        payload = deepcopy(self._and)
        payload["$and"].extend([{**d} for d in [self._or, self._not, self._xor] if d])
        return {"name": self._name, "gates": json.dumps({**payload})}

    def And(self, ids: list):
        """
        """
        for val in self._make_list(ids):
            self._and["$and"].append(val)
        return self

    def Or(self, ids: list):
        """TODO: Docstring for or.

        """
        for val in self._make_list(ids):
            self._or["$or"].append(val)
        return self

    def Not(self, ids):
        """
        """
        for val in self._make_list(ids):
            self._not["$not"].append(val)
        return self

    def Xor(self, ids):
        """
        """
        for val in self._make_list(ids):
            self._xor["$xor"].append(val)
        return self
