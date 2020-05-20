import cellengine as ce
from cellengine.payloads.population import _Population


class Population(_Population):
    @classmethod
    def get(cls, experiment_id: str, _id: str = None, name: str = None):
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_population(experiment_id, **kwargs)

    @classmethod
    def create(cls, experiment_id: str, compensation: dict):
        return ce.APIClient().post_population(experiment_id, compensation)

    def update(self):
        """Save any changed data to CellEngine."""
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "populations", self._properties
        )
        self._properties.update(res)

    def delete(self):
        ce.APIClient().delete_entity(self.experiment_id, "populations", self._id)
