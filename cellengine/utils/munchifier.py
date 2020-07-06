from munch import Munch, munchify


def get_prop(instance, key):
    """Return an attribute-style dict of the prop.
    """
    prop = instance._properties[key]
    if type(prop) is not Munch:
        instance._properties[key] = munchify(prop)
    return prop
