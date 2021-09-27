def readonly(obj, attribute, _):
    raise AttributeError(f"{attribute.name} is read-only and cannot be set for {obj.__class__}.")

