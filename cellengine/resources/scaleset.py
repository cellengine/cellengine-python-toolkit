import cellengine as ce
from cellengine.payloads.scaleset import _ScaleSet


class ScaleSet(_ScaleSet):
    @classmethod
    def get(cls, experiment_id: str):
        return ce.APIClient().get_scaleset(experiment_id)

    def update(self):
        """Save changes to this ScaleSet to CellEngine."""
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "scalesets", self._properties
        )
        self._properties.update(res)
