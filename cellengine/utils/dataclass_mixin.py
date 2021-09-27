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


class ReadOnly:
    def __init__(self, optional=False):
        self.optional = optional
        self.block_set = False

    def keys(self):
        return []

    def values(self):
        return []

    def __set_name__(self, owner, attr):
        self.owner = owner.__name__
        self.attr = attr

    def __get__(self, instance, owner):
        return getattr(instance, f"_{self.attr}")

    def __set__(self, instance, value):
        if not self.block_set or not hasattr(instance, f"_{self.attr}"):
            self.block_set = True
            if type(value) is ReadOnly:
                if self.optional:
                    setattr(instance, f"_{self.attr}", None)
                else:
                    raise AttributeError(
                        f"Property '{self.attr}' is required for object '{self.owner}'."
                    )
            else:
                setattr(instance, f"_{self.attr}", value)
        else:
            raise AttributeError(f"{self.owner}.{self.attr} cannot be set.")
