from attr import has, fields
from datetime import datetime
from cattr.converters import GenConverter
from cattr.gen import make_dict_unstructure_fn, make_dict_structure_fn, override
from cellengine.utils.helpers import datetime_to_timestamp, to_camel_case


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

    converter.register_unstructure_hook(datetime, datetime_to_timestamp)

    return converter


converter = get_converter()
