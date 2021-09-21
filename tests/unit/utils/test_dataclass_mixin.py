import pytest
from dataclasses import dataclass, field
import json

from dataclasses_json.cfg import config
from cellengine.utils.dataclass_mixin import DataClassMixin, ReadOnly


@dataclass
class DC(DataClassMixin):
    _id: str = field(metadata=config(field_name="_id"))
    foo: int
    prop: str = field(default=ReadOnly())  # type: ignore
    optional_prop: str = field(default=ReadOnly(optional=True))  # type: ignore


def test_should_deserialize_from_dict():
    data = {"_id": "some-id", "foo": 9, "prop": "some prop"}
    t = DC.from_dict(data)
    assert t.prop == "some prop"


def test_should_deserialize_from_json():
    data = {"_id": "some-id", "foo": 9, "prop": "some prop"}
    t = DC.from_json(json.dumps(data))
    assert t.prop == "some prop"


def test_should_serialize_to_dict():
    data = {"_id": "some-id", "foo": 9, "prop": "some prop"}
    t = DC.from_dict(data)
    assert t.to_dict() == data


def test_should_serialize_to_json():
    data = {"_id": "some-id", "foo": 9, "prop": "some prop"}
    t = DC.from_dict(data)
    assert t.to_json() == json.dumps(data)


def test_should_not_allow_setting_readonly_property():
    data = {"_id": "some-id", "foo": 9, "prop": "some prop"}
    t = DC.from_dict(data)
    with pytest.raises(AttributeError):
        t.prop = "something else"


def test_optional_readonly_property_should_be_none():
    data = {"_id": "some-id", "foo": 9, "prop": "some prop"}
    t = DC.from_dict(data)
    assert t.optional_prop == None
