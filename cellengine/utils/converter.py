from attr import define, has, fields
from cattr.converters import GenConverter
from cattr.gen import make_dict_unstructure_fn, make_dict_structure_fn, override

@define
class Foo:
    pass

def get_converter():
    converter = GenConverter()

    def to_snake_case(s: str) -> str:
        if s == "_id":
            return s
        return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')

    def to_camel_case(snake_str: str) -> str:
        if snake_str == "_id":
            return snake_str
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    def to_camel_case_unstructure(cls):
        return make_dict_unstructure_fn(
            cls,
            converter,
            **{
                a.name: override(rename=to_camel_case(a.name))
                for a in fields(cls)
            }
        )

    def to_camel_case_structure(cls):

        return make_dict_structure_fn(
            cls,
            converter,
            **{
                a.name: override(rename=to_camel_case(a.name))
                for a in fields(cls)
            }
    )

    converter.register_unstructure_hook_factory(
        has, to_camel_case_unstructure
    )
    converter.register_structure_hook_factory(
        has, to_camel_case_structure
    )

    def _structure_gates(*args, **kwargs):
        pass

    converter.register_structure_hook_func(
        lambda cls: issubclass(getattr(cls, '__origin__', bool), Foo),
        _structure_gates,
    )

    return converter

converter = get_converter()
