import importlib
from typing import Dict, Union, List
from collections import OrderedDict


ATTACHMENT = {"experimentId", "filename", "md5", "size"}
COMPENSATION = {"channels", "experimentId", "name", "spillMatrix"}
EXPERIMENT = {"created", "deleted", "primaryResearcher"}
FCSFILE = {
    "__v",
    "_id",
    "annotations",
    "eventCount",
    "experimentId",
    "filename",
    "hasFileInternalComp",
    "md5",
    "panel",
    "panelName",
    "size",
}
GATE = {"type", "gid", "xChannel", "yChannel"}
POPULATION = {"gates", "name", "parentId", "terminalGateGid", "uniqueName"}
SCALESET = {"scales"}

# This has to be an ordered dict because FcsFile will match Attachment
# but the reverse is not true
class_keys = OrderedDict()
class_keys["Compensation"] = COMPENSATION
class_keys["Experiment"] = EXPERIMENT
class_keys["FcsFile"] = FCSFILE
class_keys["Gate"] = GATE
class_keys["Population"] = POPULATION
class_keys["ScaleSet"] = SCALESET
class_keys["Attachment"] = ATTACHMENT


class ResourceFactory:
    @classmethod
    def load(self, properties: Union[List, Dict]):
        """Instantiates a CellengineClass.
        Args:
            properties (Dict): JSON from the Cellengine API.

        Returns:
            An instance of a class corresponding to the given dict.
        """
        if type(properties) is list:
            classname = self._match_class(properties[0])
            return [self._load_class(classname)(properties=prop) for prop in properties]
        elif type(properties) is dict:
            classname = self._match_class(properties)
            return self._load_class(classname)(properties)

    # classname = evaluate_classname(classname)
    # if type(content) is dict:
    #     return classname(properties=content)
    # elif type(content) is list:
    #     return [classname(properties=item) for item in content]

    @classmethod
    def _load_class(self, classname: str) -> type:
        module = importlib.import_module("cellengine")
        return getattr(module, classname)

    @classmethod
    def _match_class(self, properties: Dict) -> str:
        return next(
            key
            for (key, val) in class_keys.items()
            if self._keys_match(properties, val)
        )

    @classmethod
    def _keys_match(self, properties: Dict, keys: set) -> bool:
        return keys.intersection(set(properties.keys())) == keys
