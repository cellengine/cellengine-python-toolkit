import cellengine as ce
from cellengine.payloads.compensation import _Compensation


class Compensation(_Compensation):
    """A class representing a CellEngine compensation matrix. Can be applied to
    FCS files to compensate them.
    """

    @classmethod
    def get(cls, experiment_id: str, _id: str = None, name: str = None):
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_compensation(experiment_id, **kwargs)

    @classmethod
    def create(cls, experiment_id: str, compensation: dict):
        return ce.APIClient().post_compensation(experiment_id, compensation)

    def update(self):
        props = ce.APIClient().update_entity(
            self.experiment_id, self._id, "compensations", body=self._properties
        )
        self._properties.update(props)

    def delete(self):
        return ce.APIClient().delete_entity(
            self.experiment_id, "compensations", self._id
        )
