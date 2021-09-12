from dataclasses_json import DataClassJsonMixin
import dataclasses_json


class DataClassMixin(DataClassJsonMixin):
    """Mixin to use dataclasses_json for serialization/deserialization of CE entities.

    Extends the DataClassJsonMixin to support camelCase -> snake_case."""

    dataclass_json_config = dataclasses_json.config(  # type: ignore
        letter_case=dataclasses_json.LetterCase.CAMEL,  # type: ignore
        undefined=dataclasses_json.Undefined.EXCLUDE,
        # Don't encode None values with to_dict or to_json
        exclude=lambda f: f is None,  # type: ignore
    )["dataclasses_json"]
