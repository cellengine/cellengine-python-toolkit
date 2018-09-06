# API Client

[CellEngine API](https://docs.cellengine.com/api/)

The CellEngine `APIClient` object is the interface between the CellEngine API
and entities in the Python SDK. After authenticating, you may either use the
`APIClient` directly or interact with the SDK entities.

Assuming you have instantiated the `APIClient` object like...
```python
import cellengine
client = cellengine.APIClient("username")
# Password: <enter your password here>

# Alternatively, authenticate by setting CELLENGINE_PASSWORD or CELLENGINE_AUTH_TOKEN in your environment
```
...then the following sequences of commands are
equivalent:

```python
exp = client.get_experiment(name="my experiment")
fcsfile = client.get_fcsfile(experiment_id=exp._id, name="my fcs file")
```

```python
exp = cellengine.Experiment.get(name="my experiment")
fcsfile = cellengine.FcsFile.get(experiment_id=exp._id, name="my fcs file")
```

```python
exp = cellengine.Experiment.get(name="my experiment")
fcsfile = exp.get_fcs_file(name="my fcs file")
```

The `APIClient` provides many useful [methods](#methods) for interacting with
CellEngine. It also provides `_get`, `_post`, `_patch`, and `_delete` methods
for batteries-not-included interaction with the [CellEngine
API](https://docs.cellengine.com/api/). If there is a feature you do not see,
please feel free to [make a pull request][contributing] or [create an Issue on
GitHub](https://github.com/primitybio/cellengine-python-toolkit/issues).

## Methods

::: cellengine.APIClient
    rendering:
      show_root_heading: true
      show_object_full_path: false
      show_source: false
      show_if_no_docstring: true
    selection:
      filters: ["!^_"]

## Properties
- base_url
- user_name
- password
- token
- user_id
- admin
- flags
- authenticated
- cache_info
- cache_clear
