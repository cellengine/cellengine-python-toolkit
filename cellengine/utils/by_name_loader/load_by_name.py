from functools import lru_cache, wraps
from typing import List


def by_name(path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client = args[0]
            if "name" in kwargs:
                name = kwargs["name"]
                _id = _lookup_by_name(client, path, name)
                return func(*args, _id=_id)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


@lru_cache(maxsize=None)
def _lookup_by_name(client, path, name):
    if name == "fcsfiles":
        query = "filename"
    else:
        query = "name"
    if path != "experiments":
        url = f"{client.endpoint_base}/experiments/{path}"
    else:
        url = f"{client.endpoint_base}/experiments"
    content = _handle_response(
        client._get(url, params={"query": f'eq({query}, "{name}")&limit=2'})
    )
    return content["_id"]


def _handle_response(response):
    if type(response) is list:
        _handle_list(response)
    else:
        response = [response]
    return response[0]


def _handle_list(response: List) -> RuntimeError:
    if len(response) == 0:
        raise RuntimeError("No objects found.")
    elif len(response) > 1:
        raise RuntimeError("Multiple objects found; use _id to query instead.")
