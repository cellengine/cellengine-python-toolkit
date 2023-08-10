from __future__ import annotations
from typing import Optional, Any, Union, Dict

import cellengine as ce


class Population:
    def __init__(self, properties: Dict[str, Any]):
        self._properties = properties
        self._changes = set()

    @property
    def _id(self) -> str:
        return self._properties["_id"]

    @property
    def id(self) -> str:
        """Alias for ``_id``."""
        return self._properties["_id"]

    @property
    def experiment_id(self) -> str:
        return self._properties["experimentId"]

    @property
    def name(self) -> str:
        return self._properties["name"]

    @name.setter
    def name(self, value: str):
        self._properties["name"] = value
        self._changes.add("name")

    @property
    def gates(self) -> str:
        return self._properties["gates"]

    @gates.setter
    def gates(self, value: str):
        self._properties["gates"] = value
        self._changes.add("gates")

    @property
    def parent_id(self) -> Union[str, None]:
        return self._properties["parentId"]

    @parent_id.setter
    def parent_id(self, value: Union[str, None]):
        self._properties["parentId"] = value
        self._changes.add("parentId")

    @property
    def terminal_gate_gid(self) -> Union[str, None]:
        return self._properties["terminalGateGid"]

    @terminal_gate_gid.setter
    def terminal_gate_gid(self, value: Union[str, None]):
        self._properties["terminalGateGid"] = value
        self._changes.add("terminalGateGid")

    @property
    def unique_name(self) -> str:
        """The unique name for this population (has ancestor names prepended and
        numerical suffixes appended until the name is unique).

        This value is calculated by CellEngine; if the population is renamed,
        this value will not be correct until `pop.update()` is called."""
        return self._properties["uniqueName"]

    def __repr__(self):
        return f"Population(_id='{self._id}', name='{self.name}')"

    @classmethod
    def get(
        cls, experiment_id: str, _id: Optional[str] = None, name: Optional[str] = None
    ) -> Population:
        """Get Population by name or ID for a specific experiment. Either
        `name` or `_id` must be specified.

        Args:
            experiment_id: ID of the experiment this attachment is connected with.
            _id (optional): ID of the attachment.
            name (optional): Name of the experiment.
        """
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_population(experiment_id, **kwargs)

    # TODO classmethod create

    def update(self) -> None:
        """Save changes to this Population to CellEngine."""
        update_properties = {key: self._properties[key] for key in self._changes}
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "populations", update_properties
        )
        self._properties = res
        self._changes = set()

    def delete(self) -> None:
        ce.APIClient().delete_entity(self.experiment_id, "populations", self._id)
