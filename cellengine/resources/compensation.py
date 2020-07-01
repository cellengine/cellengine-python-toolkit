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

    def update(self, inplace=True):
        """Save changes to this Compensation to CellEngine.

        Args:
            inplace (bool): Update this entity or return a new one.

        Returns:
            Experiment or None: If inplace is True, returns a new Compensation.
            Otherwise, updates the current entity.
            """
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "compensations", body=self._properties
        )
        if inplace:
            self._properties.update(res)
        else:
            return self.__class__(res)

    def delete(self):
        return ce.APIClient().delete_entity(
            self.experiment_id, "compensations", self._id
        )
