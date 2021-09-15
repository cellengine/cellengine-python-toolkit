from __future__ import annotations
from dataclasses import field
from typing import Optional

from dataclasses_json.cfg import config
from cellengine.utils.dataclass_mixin import DataClassMixin, ReadOnly

from dataclasses import dataclass
import cellengine as ce


@dataclass
class Population(DataClassMixin):
    name: str
    gates: str
    parent_id: Optional[str] = None
    terminal_gate_gid: Optional[str] = None
    _id: str = field(
        metadata=config(field_name="_id"), default=ReadOnly()
    )  # type: ignore
    experiment_id: str = field(default=ReadOnly())  # type: ignore
    unique_name: str = field(default=ReadOnly())  # type: ignore

    def __repr__(self):
        return f"Population(_id='{self._id}', name='{self.name}')"

    @classmethod
    def get(cls, experiment_id: str, _id: str = None, name: str = None):
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_population(experiment_id, **kwargs)

    @classmethod
    def create(cls, experiment_id: str, population: dict) -> Population:
        return ce.APIClient().post_population(experiment_id, population)

    def update(self):
        """Save changes to this Population to CellEngine."""
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "populations", self.to_dict()
        )
        self.__dict__.update(res)

    def delete(self):
        ce.APIClient().delete_entity(self.experiment_id, "populations", self._id)
