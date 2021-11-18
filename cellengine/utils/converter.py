from cellengine.utils.helpers import (
    datetime_to_timestamp,
    timestamp_to_datetime,
    to_camel_case,
)
from datetime import datetime
from cellengine.utils.scale_utils import ScaleDict
from attr import has, fields
from cattr.converters import GenConverter
from cattr.gen import make_dict_unstructure_fn, make_dict_structure_fn, override


def get_converter():
    converter = GenConverter()

    def to_camel_case_unstructure(cls):
        return make_dict_unstructure_fn(
            cls,
            converter,
            **{a.name: override(rename=to_camel_case(a.name)) for a in fields(cls)}
        )

    def to_camel_case_structure(cls):
        return make_dict_structure_fn(
            cls,
            converter,
            **{a.name: override(rename=to_camel_case(a.name)) for a in fields(cls)}
        )

    converter.register_unstructure_hook_factory(has, to_camel_case_unstructure)
    converter.register_structure_hook_factory(has, to_camel_case_structure)

    converter.register_unstructure_hook(
        datetime, lambda dt: datetime_to_timestamp(dt)  # type: ignore
    )
    converter.register_structure_hook(datetime, lambda ts, _: timestamp_to_datetime(ts))

    converter.register_structure_hook(
        ScaleDict,
        lambda scales, _: {
            item["channelName"]: ScaleDict(item["scale"]) for item in scales
        },
    )
    converter.register_unstructure_hook(
        ScaleDict,
        lambda scales: [
            {"channelName": key, "scale": val} for key, val in scales.items()
        ],
    )

    return converter


converter = get_converter()
