from typing import List
from cellengine.payloads.gate_utils.utils import format_common_gate


class RectangleGate:
    def create(
        self,
        experiment_id: str,
        x_channel: str,
        y_channel: str,
        name: str,
        x1: float,
        x2: float,
        y1: float,
        y2: float,
        label: List[str] = [],
        gid: str = None,
        locked: bool = False,
        parent_population_id: str = None,
        parent_population: str = None,
        tailored_per_file: bool = False,
        fcs_file_id: str = None,
        fcs_file: str = None,
        create_population: bool = True,
    ):
        if label == []:
            label = [numpy.mean([x1, x2]), numpy.mean([y1, y2])]
        if gid is None:
            gid = generate_id()

        model = {
            "locked": locked,
            "label": label,
            "rectangle": {"x1": x1, "x2": x2, "y1": y1, "y2": y2},
        }

        body = {
            "experimentId": experiment_id,
            "name": name,
            "type": "RectangleGate",
            "gid": gid,
            "xChannel": x_channel,
            "yChannel": y_channel,
            "parentPopulationId": parent_population_id,
            "model": model,
        }

        return format_common_gate(
            experiment_id,
            body=body,
            tailored_per_file=tailored_per_file,
            fcs_file_id=fcs_file_id,
            fcs_file=fcs_file,
            create_population=create_population,
        )
